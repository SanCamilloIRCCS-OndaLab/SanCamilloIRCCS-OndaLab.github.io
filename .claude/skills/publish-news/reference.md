# ONDA Lab site - reference rules

Ported from the Cowork `update-lab-site` skill. `SKILL.md` says *when* to do
things; this file says *how*.

- **Publications** all live in one list, driven by `publications.xlsx`. The
  monthly batch never turns papers into post pages; a `[paper]` post is made
  only when Giorgio asks for one (`/publish-news doi:...`).
- **Activities** (talks, posters, seminars, events, defenses, awards) become
  **one post page each**.

## Repo map

| Path | What it is |
|---|---|
| `publications.xlsx` | Source of truth for the publication list. Edit this, never the yml. |
| `scripts/pubs_xlsx.py` | The only way to edit the xlsx: writes by column name, skips duplicates. |
| `scripts/fetch_new_pubs.py` | Finds candidate papers (PubMed, Europe PMC, Crossref preprints). |
| `xlsx_to_yml.py` | Converts the xlsx to `publications.yml`. Also runs as Quarto pre-render. |
| `publications.yml` | Generated. Do not hand-edit. |
| `pub-listing.qmd` | Renders the list: sections `Peer-reviewed Journal Paper` and `Preprint`. |
| `posts/presentations/` | Talks, posters, invited lectures |
| `posts/events/` | Conferences / workshops the lab ran or hosted |
| `posts/news-title/` | News items |
| `posts/papers/` | Paper announcements (only on request) |
| `files/images/` | Post images |
| `files/profiles/` | Team photos, used as fallback post thumbnails |
| `inbox/<slug>/` | Giorgio's briefs + images (git-ignored) |
| `docs/` | Rendered output, published by GitHub Pages from `main` |

Use `python` (the Anaconda interpreter - it has openpyxl and PyYAML), not `python3`.

---

## Publications

### Find them

```bash
python scripts/fetch_new_pubs.py --since 2026-09-01    # default: last 62 days
```

It queries PubMed, Europe PMC and Crossref (Crossref `posted-content` catches
PsyArXiv/OSF, bioRxiv, medRxiv preprints), dedupes against `publications.xlsx`
by DOI and title, and writes `.lab-site-updates/new_pubs.md` and `.json`.
Google Scholar is deliberately not a source: it blocks automated access.

If a source fails, the script says so at the top of the report. Never report a
clean month when a search errored out.

### Judge them

Candidates come back as `confirmed` or `review`.

- **confirmed** - Arcara G is a co-author, or the affiliation mentions San
  Camillo / Venezia / Padova, or two or more lab members are on it. Take these.
- **review** - one lab surname matched and nothing else. **Check each one.**
  Several lab surnames are common: there is a well-known *Stefano* Zago in
  Milan, several unrelated *Lago S*, and many *Napoli E*, *Oliva G*,
  *Lazzaro G*. Open the DOI or PubMed record and read the affiliation. Most
  `review` items are false positives - say so briefly, don't list every one
  in detail. When genuinely unclear, leave it out and list it for Giorgio.
- `why` containing **PUBLISHED VERSION** - the paper is on the site as a
  Preprint and is now out in a journal. Do not add a row: run
  `set-section` (below) and update DOI / journal / volume / pages in that row.

Never add a paper you could not verify.

### Add them

Write the approved candidates (same record shape as in `new_pubs.json`) to
`.lab-site-updates/approved.json` as a JSON list, fix the metadata in the JSON
first, then:

```bash
python scripts/pubs_xlsx.py add .lab-site-updates/approved.json
python scripts/pubs_xlsx.py add --doi 10.xxxx/yyyy          # single paper
python scripts/pubs_xlsx.py set-section <DOI or title> "Peer-reviewed Journal Paper"
python xlsx_to_yml.py --force                               # must say "Validated: N entries"
```

Metadata rules (fix in the JSON before adding):

- `section`: omit (the script uses `Preprint` for preprints, otherwise
  `Peer-reviewed Journal Paper`).
- `authors`: list of `Surname Initials` - `["Lago S", "Zago S", "Arcara G"]`.
  The script joins them with commas and **no space**, which the renderer expects.
- `journal`: full Title Case name - `Clinical Neurophysiology`,
  `Neurological Sciences`, `European Journal of Neurology` - not the PubMed
  lowercase or abbreviation. The script strips `" : official journal of ..."`
  subtitles but does not fix casing. Preprints: the server (`PsyArXiv`, `bioRxiv`).
- Leave unknown fields empty. Do not invent page numbers.

---

## Posts

For each activity you need **who, what, where, when**. Ask for whatever is
missing rather than guessing. Never invent a venue, a date or a co-author.

| Brief `type` | Folder | `categories` | `author` |
|---|---|---|---|
| talk, poster, invited lecture | `posts/presentations/` | `[presentation]` | the member's name |
| event the lab ran or hosted | `posts/events/` | `[event]` | the member's name |
| news: defense, award, new member, milestone | `posts/news-title/` | `[news]` | `News` |
| paper (only on request) | `posts/papers/` | `[paper]` | first lab author |

Create the folder if it does not exist. Filename = the inbox slug:
`posts/presentations/lago-sip-2026.qmd`. Read an existing sibling post first
and follow its shape.

```yaml
---
title: "Aperiodic EEG activity in healthy aging"
description: "Poster presented at the SIP Congress 2026 in Rome."
author: "Sara Lago"
date: "2026-09-24"
categories: [presentation]
image: "/files/images/lago-sip-2026-1.jpg"
draft: true
---

Two to four sentences from the brief, in English, plain prose. Link the event
site or slides if the brief gives a URL.

![Sara at the poster session](/files/images/lago-sip-2026-1.jpg)

<!--Include social share buttons-->

{{< include /files/includes/_socialshare.qmd >}}
```

### Images

- Copy each image listed in the brief from `inbox/<slug>/` to
  `files/images/<slug>-<N>.<ext>` (N = 1, 2, ... in brief order; lowercase ext).
  The first one is the listing thumbnail (`image:`); all of them go in the body
  with their captions as alt text.
- Before copying, check the size: if an image is wider than 1600 px or larger
  than 1 MB, downscale it (`sips -Z 1600 file` on macOS) - the site repo is
  public and every image is committed.
- No images in the brief: use the person's photo from `files/profiles/` (check
  the real filename - e.g. `Sara-Lago.jpg`, `giorgio_profile.jpg`), and report
  the post as **waiting for image**. If there is no profile photo either, use
  `/files/images/ONDA_waves.png`. Never point at a file that does not exist - a
  broken path breaks the listing thumbnail.
- Re-running on the same slug when new images arrive: update the existing post
  in place (replace the fallback thumbnail, add the images), don't create a second post.

### Paper posts (`/publish-news doi:...`)

Title = paper title; description = one sentence on the finding; body = a short
plain-language summary (from the abstract - fetch it from the DOI / PubMed),
the full reference, and a DOI link. Make sure the paper is also in the xlsx.
