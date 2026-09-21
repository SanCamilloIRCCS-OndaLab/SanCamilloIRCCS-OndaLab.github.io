# ONDA Lab site: update workflow

An agent keeps the lab website up to date: the publication list, and news posts about new papers and about talks, posters and conferences. It only **drafts**. Nothing is committed until you commit it, and nothing is published until you push to `main`.

## The inbox: your only input for talks and events

**`inbox/`** (at the root of the site repo) is how you hand material to the agent. The agent never goes looking for talks, posters, conferences, awards or defenses: **if it isn't in `inbox/`, no post is made.**

    inbox/
      _template/brief.md       <- copy this to start
      zago-2026-sipf/          <- one folder per item: surname-year-event
        brief.md               <- template or plain text
        photo1.jpg             <- images, any names; the first is the thumbnail

- **One folder per news item.** Name it `surname-year-event`, lowercase with dashes. The folder name also becomes the post's filename.
- **`brief.md` must say who, what, where and when.** Links, a description and image captions are optional. Plain free text works as well as the template. If something is missing, the agent asks instead of guessing.
- **Images** go in the same folder. Big photos are shrunk automatically. If there are none, the post uses the person's profile photo and the agent flags it as "waiting for image".
- **Images arrive later?** Drop them in the same folder and run `/draft-2-news inbox/<slug>` again. The same post is updated.
- **It's private.** The folder is git-ignored, so briefs and original photos are never committed or published. Only the post made from them is, once you commit it.
- **Paper posts** don't need an inbox folder: they come from `publications.xlsx`. A folder named after the paper can still add extra text or a figure.

## The three commands

| Command | Input | Output | Page on the site |
|---|---|---|---|
| `/update-publications` | Online search (PubMed, Europe PMC, Crossref) | New rows in `publications.xlsx` | Research → Publications |
| `/pub-2-news` | Papers in `publications.xlsx` not yet announced | A draft news post per paper you pick | About → News |
| `/draft-2-news` | A folder in `inbox/` | A draft news post | About → News |

**`/update-publications`**
- `monthly`: searches for papers since the start of last month. It shows you what to add, what needs your decision, and how many namesakes it rejected, then **waits for your OK**.
- `doi:<DOI>`: adds one paper to the list.

**`/pub-2-news`**
- With no argument, it lists every paper in the xlsx that has no news post yet. That includes papers you typed into the Excel file by hand. For each one you answer:
  - **post**: it drafts the post;
  - **skip**: the paper is never offered again (it's recorded in `.claude/pub-news-skip.txt`);
  - **later**: it's offered again next time.
- `<DOI>`: announces that specific paper.
- The first time you run it, all 11 existing papers are offered. Answer "skip all" if you don't want posts for them.

**`/draft-2-news`**
- `inbox/<slug>`: drafts the post for that folder.
- With no argument, it lists the inbox folders and their status (no post yet / new images / drafted / published) and offers to draft the pending ones.

**"finalize"** (say it after reviewing drafts, with any of the commands)
- Removes `draft: true`, regenerates the publication list, and rebuilds the site with `quarto render`.
- It stops there: you commit and push yourself.

**News folder.** Every post goes to `posts/news-title/` (About → News), tagged `news` and signed "News". `posts/presentations/` is for your own slide decks, which you add by hand. The agent never writes there.

**Drafts.** A new post has `draft: true`. It is built, but **not listed on the News page**. To see it, open the address in the agent's summary, for example `http://localhost:<port>/posts/news-title/<slug>.html` while `quarto preview` runs.

**Where the commands work.** In a Claude Code session opened on the site repo, or on its parent folder while you work on repo files.

## What you do

**Every month.** On the 1st, a Notion task in TASKS and a Google Calendar alert remind you. Then:
1. Read the report in the Notion task.
2. **Papers into the list:** run `/update-publications monthly`, decide on the uncertain ones, and confirm.
3. **Posts about papers:** run `/pub-2-news` and choose post, skip or later for each.
4. **Talks and events:** create the `inbox/` folders (see "The inbox" above), then run `/draft-2-news`.
5. Check with `quarto preview` and the Source Control diff. Ask for changes if needed.
6. Say "finalize", then commit and push, which publishes the site.
7. Mark the Notion task Completato.

**Anytime**
- A talk or event just happened: add an inbox folder, then run `/draft-2-news inbox/<slug>`.
- A paper just came out: run `/update-publications doi:<DOI>`, then `/pub-2-news <DOI>` if you want a post about it.
- You added a paper to the Excel file by hand: run `/pub-2-news`.

## What the agent will never do
- Commit, push, or open PRs or issues. The repo is public.
- Write posts anywhere but `posts/news-title/`.
- Add a paper it couldn't verify, or invent a venue, a date or a co-author.
- Look for talks or events itself: they come only from `inbox/`.

## Pipeline at a glance

    1st of month, 08:00 (cloud)           You                                 VS Code (local)
    ───────────────────────────           ───                                 ───────────────
    search PubMed / EuropePMC / Crossref
    → Notion task (report)          ───►  read report
    → Calendar event (reminder)     ───►  decide doubtful papers      ───►    /update-publications monthly
                                                                               · new rows in publications.xlsx
                                          post / skip / later         ───►    /pub-2-news
                                                                               · paper posts (draft)
                                          inbox/<slug>/ folders       ───►    /draft-2-news
                                                                               · talk/event posts (draft)
                                          quarto preview + diff       ◄───    · summary + preview addresses
                                          "finalize"                  ───►    · removes draft, renders docs/
                                          git commit + push (site live)
                                          mark Notion task Completato

## Example: October 2026 update

**1. Oct 1, 08:00: the routine runs.** The Notion task "Aggiornamento sito ONDA – 2026-10" appears, with this report:

    Ready to add (2)
    - Lago S,Zago S,Arcara G (2026). Aperiodic EEG and ... Clinical Neurophysiology. doi:10.1016/...
    - Tonin A,...,Arcara G (2026). [Preprint] ... PsyArXiv. doi:10.31234/...
    Need your decision (1)
    - Zago S et al. (2026) ... Cortex. Affiliation Milan, possibly Stefano Zago
    To do
    - [ ] Run /update-publications monthly in VS Code (papers -> publication list)
    - [ ] Run /pub-2-news (posts about the new papers)
    - [ ] Add this month's talks / posters / conferences to inbox/, then run /draft-2-news (news)

A Calendar event, "Revisione aggiornamento sito ONDA", is set for Oct 2 at 09:00.

**2. Papers into the list.** Run `/update-publications monthly` and say "add the first two, skip the Cortex one". Two rows go into `publications.xlsx`.

**3. Posts about papers.** Run `/pub-2-news`. It lists the two new papers. You answer "post the Clinical Neurophysiology one, skip the preprint". The agent drafts `posts/news-title/lago-2026-aperiodic.qmd`, with a summary from the abstract, the reference and a DOI link. The preprint is recorded as skipped.

**4. Talks.** Sara gave a talk at the SIPF congress. You create `inbox/zago-2026-sipf/` with:

    type: talk
    who: Sara Zago
    what: Aperiodic EEG Across Aging and Neurological Disorders: A Clinical Perspective
    where: SIPF congress, Noto
    when: 2026-09-18
    description: Part of the symposium "The Aperiodic Component of EEG: ..."
    images:
      - photo1.jpg: Sara during the talk

Then run `/draft-2-news`. It lists `zago-2026-sipf: no post yet` and asks "draft it?". You say yes, and it creates `posts/news-title/zago-2026-sipf.qmd` (draft), with the photo copied to `files/images/zago-2026-sipf-1.jpg`.

**5. Review.** With `quarto preview`, open the two preview addresses from the summaries and check the Publications page. You ask "shorten the paper summary", and the agent edits it.

**6. "finalize".** The agent removes `draft: true` and renders. Both posts are now on About → News.

**7. Publish.** Commit ("October site update") and push. The site is live. Mark the Notion task Completato.

## Files

| Path (in the site repo) | What it is |
|---|---|
| `.claude/skills/update-publications/` | `/update-publications`, plus `monthly-report.md` (the monthly routine's instructions) |
| `.claude/skills/pub-2-news/` | `/pub-2-news` |
| `.claude/skills/draft-2-news/` | `/draft-2-news` |
| `.claude/site-rules.md` | Rules shared by the three commands: never commit, repo map, judging papers, Excel rules, post format, images, finalize, summary |
| `.claude/pub-news-skip.txt` | Papers you chose not to announce |
| `.claude/WORKFLOW.md` | This guide |
| `inbox/` | Your briefs and images (git-ignored, except its `README.md` and `_template/`) |
| `scripts/fetch_new_pubs.py` | Publication search (PubMed, Europe PMC, Crossref) |
| `scripts/pubs_xlsx.py` | Adds papers to `publications.xlsx` by column name and skips duplicates. `add --doi <DOI>`, `set-section <DOI> "Peer-reviewed Journal Paper"` |
| `publications.xlsx` → `publications.yml` | The publication list; the yml is regenerated, never edited |

Notes:
- **Python:** use `python` (Anaconda, which has openpyxl), not `python3`.
- **NCBI e-mail:** PubMed asks API users for a contact address. It's read from the `NCBI_EMAIL` environment variable, so it never ends up in this public repo. It's optional: `export NCBI_EMAIL="you@example.org"` in `~/.zshrc`.
- **Monthly routine:** it runs in the cloud on claude.ai and is set up after these files are pushed. It reads `monthly-report.md` from GitHub and writes only to Notion and Google Calendar, never to GitHub.
