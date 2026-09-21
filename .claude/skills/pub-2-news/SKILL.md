---
name: pub-2-news
description: Draft a single news post on the ONDA Lab website (About -> News, posts/news-title/) announcing all the publications that are in publications.xlsx but have not been announced yet - whether added by hand or by /update-publications. Use when asked to announce new papers, write news about publications, or "make posts for the new papers".
argument-hint: "[<DOI> | finalize]"
---

# /pub-2-news

New rows in `publications.xlsx` -> **one** draft news post covering all the
papers picked in this run (never one post per paper). Every post goes to
**`posts/news-title/`**, never `posts/presentations/`. This skill does not
search for papers (that is `/update-publications`) and does not handle inbox
briefs about talks (that is `/draft-2-news`).

Read **Common** and **News posts** in [site-rules.md](../../site-rules.md)
before doing anything - in particular "Paper announcements". The hard rules
there apply: never commit or push, new posts get `draft: true`.

## Pick the mode from the argument

| Argument | Mode |
|---|---|
| nothing | Find unannounced papers |
| a DOI, `doi:<DOI>`, or a doi.org URL | Announce that paper (add it with `python scripts/pubs_xlsx.py add --doi <DOI>` first if it is not in the xlsx) |
| `finalize` (or Giorgio says "finalize" after a draft) | Finalize (site-rules.md -> Finalize) |

### Find unannounced papers

1. Read `publications.xlsx` (openpyxl, by column name). A row is **announced**
   if its DOI - or, when it has none, its title - appears in:
   - the `announced-dois:` list (or a legacy `doi:` field) of any
     `posts/news-title/*.qmd`, or
   - `.claude/pub-news-skip.txt` (one DOI or title per line; `#` starts a comment).
   Only papers that are new to the site get announced. Every paper that was on
   the site before 2026-09-21 is in the skip file as `# baseline`, so it never
   comes back. Never remove those lines.
2. List the unannounced rows, newest first (by `Date`, else `Year`, else row
   order - last rows are the most recently added): `n. Title - Journal (Year) - DOI`.
   Rows with `Year` older than last year are probably old papers added by hand
   (backfill), not news: list them separately under "older papers - suggest
   skip".
3. **Wait for Giorgio's pick.** For each paper he answers:
   - **post** -> include it in the single post (below);
   - **skip** -> append `<DOI or title>  # skipped YYYY-MM-DD` to `.claude/pub-news-skip.txt`;
   - **later** -> do nothing; it will be offered again next time.
   "skip all" / "post 1,3, skip the rest" etc. are fine.
4. Summary, with the Preview lines, and the number of papers skipped / left for later.

### Draft the post

All papers picked in one run go into **one** post, following site-rules.md ->
"Paper announcements". Filename: `posts/news-title/new-papers-<YYYY-MM>.qmd`
(today's year-month; if that file exists and is still `draft: true`, add the
papers to it instead of creating a second post). A DOI argument produces the
same kind of post, with one paper. If an `inbox/<slug>/` folder about one of
the papers exists (Giorgio may add text or a figure), use its brief and images
in that paper's section.
