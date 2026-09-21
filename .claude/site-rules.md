# ONDA Lab site - shared rules

Used by three skills:

| Skill | Job | Reads |
|---|---|---|
| `/update-publications` | search for papers -> `publications.xlsx` | Common + Publications |
| `/pub-2-news` | unannounced xlsx papers -> news posts | Common + News posts (+ Publications -> Add them) |
| `/draft-2-news` | `inbox/` briefs -> news posts | Common + News posts |

Workflow guide for Giorgio: [WORKFLOW.md](WORKFLOW.md).

# Common

## Hard rules

- **Never run `git commit`, `git push`, `git switch`/`checkout`, or open PRs or
  issues.** Leave every change uncommitted; Giorgio reviews the diff and
  commits himself. The repo is public and GitHub Pages publishes `main`.
- New posts always get `draft: true`. Only "finalize" removes it.
- Never add a paper you could not verify; never invent a venue, a date or a
  co-author. Ask instead.
- Edit `publications.xlsx` only through `scripts/pubs_xlsx.py`.
- Use `python` (Anaconda: has openpyxl and PyYAML), not `python3`.

## Repo map

| Path | What it is |
|---|---|
| `publications.xlsx` | Source of truth for the publication list. Never hand-edit the yml. |
| `scripts/pubs_xlsx.py` | The only way to edit the xlsx: writes by column name, skips duplicates. |
| `scripts/fetch_new_pubs.py` | Finds candidate papers (PubMed, Europe PMC, Crossref preprints). |
| `xlsx_to_yml.py` | xlsx -> `publications.yml`. Also runs as Quarto pre-render. |
| `pub-listing.qmd` | Publications page: sections `Peer-reviewed Journal Paper` and `Preprint`. |
| `posts/news-title/` | **News** - the only folder the agent writes posts to (About -> News). |
| `posts/presentations/` | Giorgio's own slide decks (Outreach -> Presentations). **Never write here.** |
| `files/images/` | Post images |
| `files/profiles/` | Team photos, fallback thumbnails |
| `inbox/<slug>/` | Giorgio's briefs + images (git-ignored) - the only input for `/draft-2-news` |
| `.claude/pub-news-skip.txt` | Papers Giorgio chose not to announce (used by `/pub-2-news`) |
| `docs/` | Rendered site, published from `main` |

## Finalize

Only when Giorgio asks ("finalize"). For each approved draft (default: those
listed in the last summary):

1. Remove the `draft: true` line.
2. `python xlsx_to_yml.py --force`, then `quarto render` - must finish with no errors.
3. Check new posts appear in `docs/posts.html` and new papers in `docs/pub-listing.html`.
4. Summary, then stop: "review the diff in Source Control, commit, push to
   `main` - the push publishes the site".

## Summary (end every run with this)

```
Changed files (uncommitted):
  M publications.xlsx                          +2 papers
  A posts/news-title/lago-sip-2026.qmd         (draft)
  A files/images/lago-sip-2026-1.jpg
Papers added:        <titles>                  (or "none")
Left out:            <title - reason>          (or "none")
Waiting for you:     <image missing for X / field missing in brief Y>  (or "nothing")
Preview:             http://localhost:<port>/posts/news-title/lago-sip-2026.html
                     Drafts are NOT listed on the News page until you say "finalize".
Next step:           quarto preview -> check -> "finalize" -> commit & push
                     (+ any follow-up: e.g. "/pub-2-news to announce the 2 new papers")
```

Get the file list from `git status --short`, not from memory. Include the
Preview lines whenever a draft was created or updated.

# Publications

## Find them

```bash
python scripts/fetch_new_pubs.py --since 2026-09-01    # default: last 62 days
```

Queries PubMed, Europe PMC and Crossref (`posted-content` catches PsyArXiv/OSF,
bioRxiv, medRxiv preprints), dedupes against `publications.xlsx` by DOI and
title, writes `.lab-site-updates/new_pubs.md` and `.json`. Google Scholar is
deliberately not a source: it blocks automated access.

If a source fails, the script says so at the top of the report. Never report a
clean month when a search errored out.

## Judge them

- **confirmed** - Arcara G is a co-author, or the affiliation mentions San
  Camillo / Venezia / Padova, or two or more lab members are on it. Take these.
- **review** - one lab surname matched and nothing else. **Check each one.**
  Several lab surnames are common: there is a well-known *Stefano* Zago in
  Milan, several unrelated *Lago S*, and many *Napoli E*, *Oliva G*,
  *Lazzaro G*. Open the DOI or PubMed record and read the affiliation. Most
  `review` items are false positives - report them as a count, not one by one.
  When genuinely unclear, leave it out and list it for Giorgio.
- `why` containing **PUBLISHED VERSION** - the paper is on the site as a
  Preprint and is now in a journal. Do not add a row: run `set-section` and
  update DOI / journal / volume / pages in that row.

Never add a paper you could not verify.

## Add them

Write the approved candidates (same record shape as in `new_pubs.json`) as a
JSON list to `.lab-site-updates/approved.json`, fix the metadata there, then:

```bash
python scripts/pubs_xlsx.py add .lab-site-updates/approved.json
python scripts/pubs_xlsx.py add --doi 10.xxxx/yyyy          # single paper
python scripts/pubs_xlsx.py set-section <DOI or title> "Peer-reviewed Journal Paper"
python xlsx_to_yml.py --force                               # must say "Validated: N entries"
```

Metadata rules:

- `section`: omit (the script uses `Preprint` for preprints, otherwise
  `Peer-reviewed Journal Paper`).
- `authors`: list of `Surname Initials` - `["Lago S", "Zago S", "Arcara G"]`.
  Joined with commas and **no space**, which the renderer expects.
- `journal`: full Title Case - `Clinical Neurophysiology`, `Neurological
  Sciences` - not the PubMed lowercase or abbreviation. The script strips
  `" : official journal of ..."` subtitles but not casing. Preprints: the
  server (`PsyArXiv`, `bioRxiv`). After `add --doi`, check the row and fix casing.
- Leave unknown fields empty. Do not invent page numbers.

# News posts

**Every post goes to `posts/news-title/<slug>.qmd`** with `categories: [news]`
and `author: "News"` - talks, posters, conferences, awards, defenses, new
members, paper announcements alike. That is the About -> News page. The lab
member's name goes in the title and text, not in `author`. Never write to
`posts/presentations/` (Giorgio's slide decks) and do not add `[event]` unless
Giorgio asks.

For each item you need **who, what, where, when**. Ask for whatever is missing
rather than guessing. Briefs may be free text instead of the template - that is
fine. Filename = the inbox slug.

Follow the shape of the existing news posts (read `posts/news-title/post2.qmd`):

```yaml
---
title: "Sara Lago presents aperiodic EEG results at the SIP Congress"   # headline style
description: "One sentence: who did what, where."
author: "News"
date: "2026-09-24"                  # date of the event, not today
categories: [news]
image: "/files/images/lago-sip-2026-1.jpg"
draft: true
---


## Summary

Two to four sentences from the brief, in English, plain prose. Titles of talks
in italics. Link the event site or slides if the brief gives a URL.

![Sara at the poster session](/files/images/lago-sip-2026-1.jpg)

<!--Include social share buttons-->

{{< include /files/includes/_socialshare.qmd >}}
```

## Images

- Copy each image in the brief from `inbox/<slug>/` to
  `files/images/<slug>-<N>.<ext>` (brief order, lowercase ext). The first is the
  listing thumbnail (`image:`); all go in the body with their captions as alt text.
- If an image is wider than 1600 px or larger than 1 MB, downscale it first
  (`sips -Z 1600 file`) - the repo is public and every image is committed.
- No images: use the person's photo from `files/profiles/` (check the real
  filename - `Sara-Lago.jpg`, `Sara-Zago.jpg`, `giorgio_profile.jpg`...) and
  report **waiting for image**. No profile photo either:
  `/files/images/ONDA_waves.png`. Never point at a file that does not exist.
- Re-running on the same slug: update the existing post in place (replace the
  fallback thumbnail, add images), never create a second post.

## Paper announcements (`/pub-2-news`)

- Title: a headline about the paper - "New paper in NeuroImage on ...".
- Frontmatter: add **`doi: <DOI>`** (bare DOI, no URL) - this is how
  `/pub-2-news` knows the paper has been announced. `date:` = publication date
  (xlsx `Date`, else today).
- `## Summary`: two to four plain-language sentences from the abstract (fetch
  it via the DOI / PubMed - do not write from the title alone), then the full
  reference in the site's style (`Authors (Year). Title. *Journal*, vol(issue),
  pages.`) and a DOI link.
- Thumbnail: the first lab author's profile photo (Images rules for fallback),
  unless an inbox folder for the paper provides an image.
- The paper must be in the xlsx (Publications -> Add them).
