---
name: update-publications
description: Find new publications and preprints by ONDA Lab members and add them to publications.xlsx (the site's publication list), or add a single paper by DOI. Use for the monthly publication update, "check for new papers", or "add this paper to the publication list".
argument-hint: "[monthly | doi:<DOI> | finalize]"
---

# /update-publications

Keeps the publication list (`publications.xlsx` -> Publications page) up to
date. It does not make news posts - that is `/pub-2-news` (papers) and
`/draft-2-news` (inbox briefs).

Read **Common** and **Publications** in [site-rules.md](../../site-rules.md)
before doing anything. The hard rules there apply: never commit or push.

## Pick the mode from the argument

| Argument | Mode |
|---|---|
| `monthly` (or nothing) | Monthly search |
| `doi:<DOI>`, a DOI, or a doi.org URL | Add one paper |
| `finalize` | Finalize (site-rules.md -> Finalize) |

### Monthly search

1. `python scripts/fetch_new_pubs.py --since <first day of the previous month>`
   (or the date Giorgio gives). Read `.lab-site-updates/new_pubs.json`. If any
   source failed, say so first.
2. Judge the candidates (Publications -> Judge them). Show a short list:
   **to add** (title - journal - why), **published versions of preprints**,
   **need your decision** (with reason), and one line counting the homonyms
   you rejected.
3. **Wait for Giorgio's confirmation**, then add the approved papers
   (Publications -> Add them) and run `python xlsx_to_yml.py --force`.
4. Summary (site-rules.md). Then remind him: `/pub-2-news` drafts posts about
   the new papers; talks and conferences go through `inbox/` + `/draft-2-news`.

### Add one paper

1. `python scripts/pubs_xlsx.py add --doi <DOI>` (skips it if already present).
2. Check the new row: journal casing, author format, Section. Fix via the
   JSON route if needed. `python xlsx_to_yml.py --force`.
3. Summary. If Giorgio also wants a news post about it: `/pub-2-news <DOI>`.
