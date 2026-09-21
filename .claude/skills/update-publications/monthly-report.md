# Monthly report - instructions for the scheduled cloud routine

You are the monthly ONDA Lab site check, running unattended in the cloud on a
clone of the public site repo. Your only outputs are **one Notion task and one
Google Calendar event**, both private to Giorgio.

## Never

- Edit, commit or push files; open PRs or issues; post anything anywhere
  public. The repo is public and nothing about unverified papers belongs there.
- Add papers to the site. That happens later, locally, with `/update-publications monthly`.

## Steps

1. `pip install openpyxl` if it is missing, then run
   `python scripts/fetch_new_pubs.py --since <first day of the previous month>`
   and read `.lab-site-updates/new_pubs.json`.
2. Judge the candidates following [site-rules.md](../../site-rules.md) (Publications -> "Judge them").
   For `review` items, open the DOI / PubMed record and read the affiliations.
   Sort every candidate into: **ready to add**, **published version of a
   preprint**, **needs Giorgio's decision** (with the reason), or **not ours**
   (count only).
3. Create a page in the Notion data source `collection://251556dd-8f75-801c-bb51-000befdfe04f`
   (database "🏃🏻 TASKS") with these properties:

   | Property | Value |
   |---|---|
   | Nome Task | `Aggiornamento sito ONDA – YYYY-MM` (current month) |
   | Status | `Non Iniziato` |
   | Active | `Active (you)` |
   | Macrogruppo | `Ricerca` |
   | Gruppo | `Ricerca - Altro` |
   | Effort level | `Small` |
   | Data promemoria | today (date only) |
   | Data Deadline | today + 7 days (date only) |
   | NOTE | one line, e.g. `3 nuovi paper, 1 da verificare` |

   Page body, in English, short:

   ```
   ## Ready to add (N)
   - Authors (Year). Title. Journal. doi:...        <- xlsx-row style, one per paper
   ## Published versions of preprints (N)
   ## Need your decision (N)
   - Title - Journal - reason (e.g. "affiliation Milan: possibly Stefano Zago")
   ## Not ours: N candidates rejected (homonyms)
   ## Search problems
   (any source that failed - or "none")
   ## To do
   - [ ] Run /update-publications monthly in VS Code (papers -> publication list)
   - [ ] Run /pub-2-news (posts about the new papers)
   - [ ] Add this month's talks / posters / conferences to inbox/, then run /draft-2-news (news)
   - [ ] Review, finalize, commit & push
   ```

   If nothing new was found, still create the task (NOTE: `nessun nuovo paper`)
   - it is also the monthly reminder for conferences and talks.
4. Create a Google Calendar event on Giorgio's primary calendar: **"Revisione
   aggiornamento sito ONDA"**, next working day (Mon-Fri) 09:00-09:30
   Europe/Rome, description = the NOTE line plus the Notion task URL.
5. Reply with a two-line summary: the counts and the Notion task URL.
