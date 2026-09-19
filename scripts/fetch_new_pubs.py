#!/usr/bin/env python3
"""
Find publications and preprints by ONDA Lab members that are not yet on the lab site.

Sources
  PubMed (NCBI E-utilities)  - peer-reviewed, authoritative metadata
  Europe PMC                 - peer-reviewed + bioRxiv/medRxiv/Research Square preprints
  Crossref (posted-content)  - preprint servers incl. PsyArXiv / OSF, SSRN

Dedupe reference
  publications.xlsx if present (the source of truth), otherwise publications.yml.

Output
  <outdir>/new_pubs.json  - structured candidates, for Claude to review
  <outdir>/new_pubs.md    - the same thing, readable

Usage
  python scripts/fetch_new_pubs.py                     # last 62 days
  python scripts/fetch_new_pubs.py --since 2026-01-01
  python scripts/fetch_new_pubs.py --no-crossref
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

# --------------------------------------------------------------------------
# CONFIG - edit this block when the lab changes
# --------------------------------------------------------------------------

# NCBI asks API clients to identify themselves. Put a real address here.
NCBI_TOOL = "ondalab-site-updater"
# Read from the environment so the address never lands in this public repo.
NCBI_EMAIL = os.environ.get("NCBI_EMAIL", "")

MEMBERS = [
    # pi=True means a hit with this author is always ours, no affiliation check needed
    {"name": "Giorgio Arcara",   "surname": "Arcara",   "initial": "G", "pi": True},
    {"name": "Sara Lago",        "surname": "Lago",     "initial": "S"},
    {"name": "Sara Zago",        "surname": "Zago",     "initial": "S"},
    {"name": "Giovanni Lazzaro", "surname": "Lazzaro",  "initial": "G"},
    {"name": "Alessandro Tonin", "surname": "Tonin",    "initial": "A"},
    {"name": "Ettore Napoli",    "surname": "Napoli",   "initial": "E"},
    {"name": "Giulia Oliva",     "surname": "Oliva",    "initial": "G"},
    {"name": "Daria Ardelean",   "surname": "Ardelean", "initial": "D"},
    {"name": "Castana Dassie",   "surname": "Dassie",   "initial": "C"},
]

# An unfamiliar author counts as ours if one of these shows up in their affiliation.
AFFILIATION_HINTS = [
    "san camillo", "ospedale san camillo", "venezia", "venice",
    "padova", "padua", "lido di venezia",
]

DEFAULT_LOOKBACK_DAYS = 62
POLITE_DELAY = 0.5  # seconds between API calls

# --------------------------------------------------------------------------

UA = "ondalab-site-updater/1.0 (lab website maintenance script)"


def get(url: str, tries: int = 2) -> str:
    """GET with a couple of retries; returns decoded body or raises."""
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (429, 500, 502, 503):
                time.sleep(3 * (attempt + 1))
                continue
            raise
        except Exception as exc:  # noqa: BLE001 - network flakiness
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"GET failed after {tries} tries: {url} ({last})")


def norm_title(title: str) -> str:
    """Aggressive normalisation so 'A Study: Part 1.' == 'a study part 1'."""
    t = (title or "").lower()
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def norm_doi(doi: str | None) -> str:
    if not doi:
        return ""
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d


# --------------------------------------------------------------------------
# what is already on the site
# --------------------------------------------------------------------------

def load_existing(repo: Path) -> tuple[set[str], set[str], str, set[str]]:
    """Titles, DOIs, source file, and titles of rows listed as Preprint."""
    xlsx = repo / "publications.xlsx"
    yml = repo / "publications.yml"

    if xlsx.exists():
        try:
            import openpyxl  # noqa: PLC0415
        except ImportError:
            print("openpyxl not installed; falling back to publications.yml", file=sys.stderr)
        else:
            wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
            ws = wb.active
            rows = ws.iter_rows(values_only=True)
            header = [str(c).strip().lower() if c else "" for c in next(rows)]
            ti = header.index("title") if "title" in header else None
            di = header.index("doi") if "doi" in header else None
            si = header.index("section") if "section" in header else None
            titles, dois, preprints = set(), set(), set()
            for row in rows:
                if ti is not None and ti < len(row) and row[ti]:
                    titles.add(norm_title(str(row[ti])))
                    if si is not None and si < len(row) and str(row[si] or "").strip() == "Preprint":
                        preprints.add(norm_title(str(row[ti])))
                if di is not None and di < len(row) and row[di]:
                    dois.add(norm_doi(str(row[di])))
            wb.close()
            return titles, dois - {""}, "publications.xlsx", preprints

    if yml.exists():
        try:
            import yaml  # noqa: PLC0415
            entries = yaml.safe_load(yml.read_text(encoding="utf-8")) or []
            titles = {norm_title(str(e.get("title", ""))) for e in entries if isinstance(e, dict)}
            dois = {norm_doi(str(e.get("doi", ""))) for e in entries if isinstance(e, dict)}
        except ImportError:
            text = yml.read_text(encoding="utf-8")
            titles = {norm_title(m.group(1)) for m in re.finditer(r'^\s*title:\s*"?(.+?)"?\s*$', text, re.M)}
            dois = {norm_doi(m.group(1)) for m in re.finditer(r'^\s*doi:\s*"?(.+?)"?\s*$', text, re.M)}
        return titles, dois - {""}, "publications.yml", set()

    raise SystemExit(
        "Neither publications.xlsx nor publications.yml found. "
        "Run this from the site repo, or pass --repo."
    )


# --------------------------------------------------------------------------
# sources
# --------------------------------------------------------------------------

def pubmed(member: dict, since: date) -> list[dict]:
    """esearch for PMIDs, then efetch MEDLINE and parse it."""
    term = f'{member["surname"]} {member["initial"]}[Author] AND ("{since:%Y/%m/%d}"[EDAT] : "3000"[EDAT])'
    params = {"db": "pubmed", "term": term, "retmode": "json", "retmax": "50",
              "tool": NCBI_TOOL}
    if NCBI_EMAIL:
        params["email"] = NCBI_EMAIL
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(params)
    ids = json.loads(get(url)).get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    time.sleep(POLITE_DELAY)
    fparams = {"db": "pubmed", "id": ",".join(ids), "rettype": "medline",
               "retmode": "text", "tool": NCBI_TOOL}
    if NCBI_EMAIL:
        fparams["email"] = NCBI_EMAIL
    furl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(fparams)
    return parse_medline(get(furl))


def parse_medline(text: str) -> list[dict]:
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        if not block.strip():
            continue
        fields: dict[str, list[str]] = {}
        key = None
        for line in block.splitlines():
            m = re.match(r"^([A-Z]{2,4})\s*-\s(.*)$", line)
            if m:
                key, val = m.group(1), m.group(2)
                fields.setdefault(key, []).append(val)
            elif key and line.startswith("      "):
                fields[key][-1] += " " + line.strip()
        if "TI" not in fields:
            continue
        doi = ""
        for cand in fields.get("LID", []) + fields.get("AID", []):
            if "[doi]" in cand:
                doi = cand.replace("[doi]", "").strip()
                break
        out.append({
            "source": "PubMed",
            "pmid": (fields.get("PMID") or [""])[0],
            "title": fields["TI"][0].rstrip("."),
            "authors": fields.get("AU", []),
            "journal": (fields.get("JT") or fields.get("TA") or [""])[0],
            "year": ((fields.get("DP") or [""])[0].split() or [""])[0],
            "date": (fields.get("DP") or [""])[0],
            "volume": (fields.get("VI") or [""])[0],
            "issue": (fields.get("IP") or [""])[0],
            "pages": (fields.get("PG") or [""])[0],
            "doi": doi,
            "affiliations": fields.get("AD", []),
            "is_preprint": False,
        })
    return out


def europepmc(member: dict, since: date) -> list[dict]:
    query = (f'AUTH:"{member["surname"]} {member["initial"]}" '
             f'AND FIRST_PDATE:[{since:%Y-%m-%d} TO 2100-12-31]')
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
           + urllib.parse.urlencode({"query": query, "format": "json",
                                     "resultType": "core", "pageSize": "50"}))
    data = json.loads(get(url))
    out = []
    for r in data.get("resultList", {}).get("result", []):
        affs = []
        for a in (r.get("authorList", {}) or {}).get("author", []) or []:
            for aff in (a.get("authorAffiliationDetailsList", {}) or {}).get("authorAffiliation", []) or []:
                if aff.get("affiliation"):
                    affs.append(aff["affiliation"])
        if r.get("affiliation"):
            affs.append(r["affiliation"])
        out.append({
            "source": "EuropePMC",
            "pmid": r.get("pmid", ""),
            "title": (r.get("title") or "").rstrip("."),
            "authors": [a.strip() for a in (r.get("authorString") or "").split(",") if a.strip()],
            "journal": (r.get("journalInfo", {}) or {}).get("journal", {}).get("title", "")
                       or r.get("bookOrReportDetails", {}).get("publisher", ""),
            "year": str(r.get("pubYear", "")),
            "date": r.get("firstPublicationDate", ""),
            "volume": (r.get("journalInfo", {}) or {}).get("volume", ""),
            "issue": (r.get("journalInfo", {}) or {}).get("issue", ""),
            "pages": r.get("pageInfo", ""),
            "doi": r.get("doi", ""),
            "affiliations": affs,
            "is_preprint": r.get("source") == "PPR",
        })
    return out


def crossref_preprints(member: dict, since: date) -> list[dict]:
    """posted-content = preprints: PsyArXiv/OSF, bioRxiv, medRxiv, Research Square, SSRN."""
    url = ("https://api.crossref.org/works?"
           + urllib.parse.urlencode({
               "query.author": member["name"],
               "filter": f"from-posted-date:{since:%Y-%m-%d},type:posted-content",
               "rows": "30",
               # No "select": "abstract" and "institution" are not selectable (HTTP 400),
               # and institution is where the preprint server name lives.
               **({"mailto": NCBI_EMAIL} if NCBI_EMAIL else {}),
           }))
    data = json.loads(get(url))
    out = []
    for it in data.get("message", {}).get("items", []):
        authors = []
        for a in it.get("author", []) or []:
            fam = a.get("family", "")
            given = (a.get("given") or "").strip()
            authors.append(f"{fam} {given[:1]}".strip() if fam else a.get("name", ""))
        # Crossref author queries are fuzzy; require a real surname match.
        if not any(member["surname"].lower() in a.lower() for a in authors):
            continue
        posted = it.get("posted", {}).get("date-parts", [[None]])[0]
        server = ""
        if it.get("institution"):
            server = (it["institution"][0] or {}).get("name", "")
        server = server or it.get("group-title", "") or "Preprint"
        out.append({
            "source": "Crossref",
            "pmid": "",
            "title": (it.get("title") or [""])[0].rstrip("."),
            "authors": authors,
            "journal": server,
            "year": str(posted[0]) if posted and posted[0] else "",
            "date": "-".join(str(p) for p in posted if p),
            "volume": "", "issue": "", "pages": "",
            "doi": it.get("DOI", ""),
            "affiliations": [],
            "is_preprint": True,
        })
    return out


# --------------------------------------------------------------------------
# merge + judge
# --------------------------------------------------------------------------

def is_lab_author(name: str) -> str | None:
    n = name.lower()
    for m in MEMBERS:
        s, i = m["surname"].lower(), m["initial"].lower()
        if re.search(rf"\b{re.escape(s)}\b", n) and (i in n.replace(s, "")):
            return m["name"]
    return None


def classify(rec: dict) -> tuple[str, str]:
    """Return (confidence, why). Common surnames make this necessary."""
    matched = {is_lab_author(a) for a in rec["authors"]} - {None}
    if "Giorgio Arcara" in matched:
        return "confirmed", "Arcara G is a co-author"
    aff_blob = " ".join(rec.get("affiliations") or []).lower()
    hit = next((h for h in AFFILIATION_HINTS if h in aff_blob), None)
    if hit:
        return "confirmed", f"affiliation mentions '{hit}'"
    if len(matched) >= 2:
        return "confirmed", f"{len(matched)} lab members as co-authors: {', '.join(sorted(matched))}"
    if matched:
        return "review", f"only {', '.join(sorted(matched))} matched, no affiliation confirmation"
    return "review", "no lab member or affiliation confirmed"


def _titlecase_score(name: str) -> int:
    """How 'Title Cased' a journal name looks - used to pick the nicer variant."""
    words = [w for w in (name or "").split() if len(w) > 3]
    return sum(1 for w in words if w[0].isupper()) - (0 if words else 1)


def merge(records: list[dict]) -> list[dict]:
    """One entry per paper; prefer PubMed metadata, keep affiliations from anywhere."""
    rank = {"PubMed": 0, "EuropePMC": 1, "Crossref": 2}
    by_key: dict[str, dict] = {}
    for rec in sorted(records, key=lambda r: rank.get(r["source"], 9)):
        key = norm_doi(rec["doi"]) or norm_title(rec["title"])
        if not key:
            continue
        if key in by_key:
            cur = by_key[key]
            cur["affiliations"] = list(dict.fromkeys(cur["affiliations"] + rec["affiliations"]))
            cur["also_in"] = sorted(set(cur.get("also_in", []) + [rec["source"]]))
            if len(rec["authors"]) > len(cur["authors"]):
                cur["authors"] = rec["authors"]
            for f in ("volume", "issue", "pages", "doi"):
                if not cur.get(f) and rec.get(f):
                    cur[f] = rec[f]
            # PubMed lowercases journal names ("Clinical neurophysiology");
            # Europe PMC keeps title case, which is what the site uses.
            if _titlecase_score(rec.get("journal", "")) > _titlecase_score(cur.get("journal", "")):
                cur["journal"] = rec["journal"]
            cur["is_preprint"] = cur["is_preprint"] and rec["is_preprint"]
        else:
            by_key[key] = dict(rec)
    return list(by_key.values())


def to_yaml_entry(rec: dict) -> str:
    def q(v):
        s = str(v)
        return f'"{s}"' if re.search(r'[:,#]|^\s|\s$', s) else s

    section = "Preprint" if rec["is_preprint"] else "Peer-reviewed Journal Paper"
    lines = [f"- section: {section}",
             f'  authors: "{",".join(rec["authors"])}"']
    if rec.get("year"):
        lines.append(f"  year: {rec['year']}")
    lines.append(f"  title: {q(rec['title'])}")
    if rec.get("journal"):
        lines.append(f"  journal: {q(rec['journal'])}")
    for key in ("volume", "issue", "pages"):
        if rec.get(key):
            lines.append(f"  {key}: {q(rec[key])}")
    if rec.get("doi"):
        lines.append(f"  doi: {rec['doi']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="site repo root (default: cwd)")
    ap.add_argument("--since", help="YYYY-MM-DD (default: %d days ago)" % DEFAULT_LOOKBACK_DAYS)
    ap.add_argument("--out", default=".lab-site-updates", help="output directory")
    ap.add_argument("--no-pubmed", action="store_true")
    ap.add_argument("--no-europepmc", action="store_true")
    ap.add_argument("--no-crossref", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    since = (date.fromisoformat(args.since) if args.since
             else date.today() - timedelta(days=DEFAULT_LOOKBACK_DAYS))

    known_titles, known_dois, ref, preprint_titles = load_existing(repo)
    print(f"Site currently lists {len(known_titles)} publications (from {ref}).", file=sys.stderr)
    print(f"Looking for anything new since {since:%Y-%m-%d}.\n", file=sys.stderr)

    raw: list[dict] = []
    problems: list[str] = []
    strikes: dict[str, int] = {}
    for m in MEMBERS:
        for enabled, label, fn in (
            (not args.no_pubmed, "PubMed", pubmed),
            (not args.no_europepmc, "EuropePMC", europepmc),
            (not args.no_crossref, "Crossref", crossref_preprints),
        ):
            if not enabled:
                continue
            # If a source is down or blocked, stop hammering it after 3 strikes.
            if strikes.get(label, 0) >= 3:
                continue
            try:
                found = fn(m, since)
                raw.extend(found)
                strikes[label] = 0
                print(f"  {label:<10} {m['name']:<20} {len(found):>3} hits", file=sys.stderr)
            except Exception as exc:  # noqa: BLE001
                strikes[label] = strikes.get(label, 0) + 1
                short = str(exc).split("(", 1)[-1].rstrip(")")[:120]
                if strikes[label] >= 3:
                    problems.append(
                        f"{label}: unreachable after 3 attempts, SKIPPED for all remaining "
                        f"members - results are incomplete ({short})")
                    print(f"  {label:<10} giving up on this source", file=sys.stderr)
                else:
                    problems.append(f"{label} / {m['name']}: {short}")
                    print(f"  {label:<10} {m['name']:<20} FAILED ({short})", file=sys.stderr)
            time.sleep(POLITE_DELAY)

    merged = merge(raw)
    def is_new(r: dict) -> bool:
        if norm_doi(r["doi"]) and norm_doi(r["doi"]) in known_dois:
            return False
        # A journal version of a paper the site lists as Preprint is news, not a duplicate.
        if not r["is_preprint"] and norm_title(r["title"]) in preprint_titles:
            r["published_preprint"] = True
            return True
        return norm_title(r["title"]) not in known_titles

    new = [r for r in merged if is_new(r)]

    for rec in new:
        rec["confidence"], rec["why"] = classify(rec)
        if rec.get("published_preprint"):
            rec["why"] += "; PUBLISHED VERSION of a row listed as Preprint - use set-section, do not add a new row"
        rec["yaml"] = to_yaml_entry(rec)

    new.sort(key=lambda r: (r["confidence"] != "confirmed", not r["is_preprint"], r.get("date", "")), reverse=False)

    outdir = repo / args.out
    outdir.mkdir(exist_ok=True)
    payload = {
        "generated": date.today().isoformat(),
        "since": since.isoformat(),
        "dedupe_reference": ref,
        "known_count": len(known_titles),
        "candidates": new,
        "problems": problems,
    }
    (outdir / "new_pubs.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [f"# New publications since {since:%Y-%m-%d}", "",
          f"Checked against {ref} ({len(known_titles)} entries). "
          f"{len(new)} candidate(s) not yet on the site.", ""]
    if problems:
        md += ["> Some searches failed and may hide results:", ""] + [f"> - {p}" for p in problems] + [""]
    for bucket in ("confirmed", "review"):
        rows = [r for r in new if r["confidence"] == bucket]
        if not rows:
            continue
        md += [f"## {bucket.title()} ({len(rows)})", ""]
        for r in rows:
            tag = " *(preprint)*" if r["is_preprint"] else ""
            md += [f"### {r['title']}{tag}",
                   f"- {', '.join(r['authors'])}",
                   f"- {r['journal']} {r.get('date','')} {r.get('volume','')}"
                   f"{'(' + r['issue'] + ')' if r.get('issue') else ''}"
                   f"{':' + r['pages'] if r.get('pages') else ''}".strip(),
                   f"- doi: {r['doi'] or '-'}  |  pmid: {r['pmid'] or '-'}  |  why: {r['why']}",
                   "", "```yaml", r["yaml"], "```", ""]
    (outdir / "new_pubs.md").write_text("\n".join(md), encoding="utf-8")

    print(f"\n{len(new)} candidate(s) written to {outdir}/new_pubs.md", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
