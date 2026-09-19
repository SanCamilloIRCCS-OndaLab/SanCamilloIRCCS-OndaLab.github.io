---
name: publish-news
description: Draft a news post for the ONDA Lab website (About -> News, posts/news-title/) from an inbox brief with images - talks, posters, conferences, awards, defenses, new members - or announcing a new paper by DOI. Use when asked to publish or add news, a talk, a conference or a paper announcement to the lab site.
argument-hint: "[inbox/<slug> | doi:<DOI> | pending | finalize]"
---

# /publish-news

Drafts news posts for Giorgio to review. Every post goes to
**`posts/news-title/`** (the About -> News page) - never to
`posts/presentations/`. The publication list itself is `/update-publications`.

Read **Common** and **News posts** in [site-rules.md](../../site-rules.md)
before doing anything. The hard rules there apply: never commit or push, new
posts get `draft: true`.

## Pick the mode from the argument

| Argument | Mode |
|---|---|
| `inbox/<slug>`, or a path to a `brief.md` / folder | Post from a brief |
| `doi:<DOI>`, a DOI, or a doi.org URL | Paper announcement |
| `pending` (or nothing) | Pending briefs |
| `finalize` (or Giorgio says "finalize" after a draft) | Finalize (site-rules.md -> Finalize) |

### Post from a brief

1. Read `inbox/<slug>/brief.md` (template or free text) and list the folder's
   images. If who / what / where / when is missing or ambiguous, ask first.
2. Create or update `posts/news-title/<slug>.qmd` (News posts, Images).
3. If the item is a paper, also make sure it is in the xlsx (Publications -> Add them).
4. Summary, with the Preview lines.

### Paper announcement

1. `python scripts/pubs_xlsx.py add --doi <DOI>` (skips it if already present);
   check the row's journal casing and authors; `python xlsx_to_yml.py --force`.
2. Draft `posts/news-title/<first-author-surname>-<year>-<keyword>.qmd`
   (News posts -> Paper announcements). If an `inbox/` folder for the paper
   exists, use its brief and images.
3. Summary, with the Preview lines.

### Pending briefs

List every `inbox/*/` folder (skip `_template`) with its status: **no post
yet**, **has new images since the post was made**, or **drafted** / **published**
(check `draft:` in `posts/news-title/<slug>.qmd`). Offer to draft the first
two groups; on "yes" run "Post from a brief" for each.
