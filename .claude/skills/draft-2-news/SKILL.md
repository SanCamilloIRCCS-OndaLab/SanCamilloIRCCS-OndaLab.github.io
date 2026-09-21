---
name: draft-2-news
description: Turn a brief from the inbox/ folder (talk, poster, conference, award, defense, new member...) into a draft news post on the ONDA Lab website (About -> News, posts/news-title/) for Giorgio's review. Use when asked to draft, add or publish a news item, talk or conference from the inbox.
argument-hint: "[inbox/<slug> | finalize]"
---

# /draft-2-news

Inbox brief -> draft news post. Every post goes to **`posts/news-title/`**
(the About -> News page), never `posts/presentations/`. Posts about papers are
`/pub-2-news`; the publication list is `/update-publications`.

Read **Common** and **News posts** in [site-rules.md](../../site-rules.md)
before doing anything. The hard rules there apply: never commit or push, new
posts get `draft: true`.

## Pick the mode from the argument

| Argument | Mode |
|---|---|
| `inbox/<slug>`, or a path to a `brief.md` / folder | Draft from a brief |
| nothing | Pending briefs |
| `finalize` (or Giorgio says "finalize" after a draft) | Finalize (site-rules.md -> Finalize) |

### Draft from a brief

1. Read `inbox/<slug>/brief.md` (template or free text) and list the folder's
   images. If who / what / where / when is missing or ambiguous, ask first.
2. Create or update `posts/news-title/<slug>.qmd` (News posts, Images).
3. If the brief is about a paper, stop and suggest `/pub-2-news` instead.
4. Summary, with the Preview lines.

### Pending briefs

List every `inbox/*/` folder (skip `_template`) with its status: **no post
yet**, **new images since the post was made**, **drafted** or **published**
(check `draft:` in `posts/news-title/<slug>.qmd`). Offer to draft the first two
groups; on "yes" run "Draft from a brief" for each.
