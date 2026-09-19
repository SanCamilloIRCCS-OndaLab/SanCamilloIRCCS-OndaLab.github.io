---
name: publish-news
description: Draft updates for the ONDA Lab website - add new lab publications to publications.xlsx and turn talks, posters, conferences, events and other news into post pages, from an inbox brief, a DOI, or the monthly publication search. Use when asked to publish or add news, a talk, a conference, a paper or a publication to the lab site, or to do the monthly site update.
argument-hint: "[monthly | inbox/<slug> | doi:<DOI> | finalize]"
---

# /publish-news

Drafts changes to the ONDA Lab site for Giorgio to review. How-to details
(repo map, judging candidates, xlsx rules, post format, images) are in
[reference.md](reference.md) - read it before doing anything.

## Hard rules

- **Never run `git commit`, `git push`, `git switch`/`checkout`, or open PRs or
  issues.** Leave every change uncommitted in the working tree; Giorgio
  reviews the diff and commits himself. The repo is public.
- New posts always get `draft: true`. Only `finalize` removes it.
- Never add a paper you could not verify; never invent a venue, a date or a
  co-author. Ask instead.
- Edit `publications.xlsx` only through `scripts/pubs_xlsx.py`.
- Use `python`, not `python3`.

## Pick the mode from the argument

| Argument | Mode |
|---|---|
| `monthly` | Monthly update |
| `inbox/<slug>`, or a path to a `brief.md` / folder | Post from a brief |
| `doi:<DOI>`, a DOI, or a doi.org URL | Paper news |
| `finalize` (or Giorgio says "finalize" after a draft) | Finalize |
| nothing | Ask which of the above he wants; list any `inbox/*/` folders that have no post yet |

### Monthly update

1. Run `python scripts/fetch_new_pubs.py --since <first day of the previous month>`
   (or an earlier date if Giorgio names one). Read `.lab-site-updates/new_pubs.json`.
   If any source failed, say so first.
2. Judge the candidates (reference.md, "Judge them"). Show Giorgio a short list:
   **to add** (title - journal - why), **published versions of preprints**,
   **need your decision** (with the reason), and a one-line count of the
   `review` items you rejected as other people.
3. **Wait for his confirmation**, then add the approved papers (reference.md,
   "Add them") and run `python xlsx_to_yml.py --force`.
4. For every `inbox/*/` folder (skip `_template`) that has no matching post
   yet, or has new images since the post was made: run the brief mode.
5. End with the summary (below).

### Post from a brief

1. Read `inbox/<slug>/brief.md` and list the folder's images. If who / what /
   where / when is missing, ask before writing.
2. Create or update the post as in reference.md, "Posts" - `draft: true`,
   images copied to `files/images/<slug>-N.ext`, fallback thumbnail if none.
3. If the brief's `type` is `paper`, also make sure the paper is in the xlsx.
4. End with the summary, and tell Giorgio he can check the post with
   `quarto preview` at `/posts/<folder>/<slug>.html` (drafts are not in the listing).

### Paper news

1. `python scripts/pubs_xlsx.py add --doi <DOI>` (it skips papers already
   present); check the new row's journal name and authors, fix the casing if
   needed (reference.md, metadata rules); `python xlsx_to_yml.py --force`.
2. Draft `posts/papers/<first-author-surname>-<year>-<keyword>.qmd` as in
   reference.md, "Paper posts". If an `inbox/` folder for the paper exists, use
   its brief and images.
3. End with the summary.

### Finalize

Only when Giorgio asks. For each post he approves (default: all drafts created
in this session / listed in the last summary):

1. Remove the `draft: true` line.
2. `python xlsx_to_yml.py --force`, then `quarto render`. It must finish with no errors.
3. Check the posts appear in `docs/posts.html` and new papers in `docs/pub-listing.html`.
4. Summary, then stop. Remind him: review the diff in Source Control, commit,
   push to `main` - the push is what publishes the site.

## Summary (end every run with this)

```
Changed files (uncommitted):
  M publications.xlsx          +2 papers
  A posts/presentations/lago-sip-2026.qmd   (draft)
  A files/images/lago-sip-2026-1.jpg
Papers added:        <titles>
Left out:            <title - reason>    (or "none")
Waiting for you:     <image missing for X / missing field in brief Y>  (or "nothing")
Next step:           quarto preview -> say "finalize" -> commit & push
```

Get the file list from `git status --short`, not from memory.
