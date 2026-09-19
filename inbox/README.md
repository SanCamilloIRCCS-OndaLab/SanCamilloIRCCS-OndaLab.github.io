# inbox/

Drop material for a news item here, one folder per item. Everything in this
folder except this README and `_template/` is git-ignored: nothing you put here
is published until `/publish-news` turns it into a post and you commit.

    inbox/
      _template/brief.md       <- copy this
      lago-sip-2026/           <- one folder per item, short slug: surname-event-year
        brief.md
        poster.jpg             <- images, any names, listed in brief.md

Then, in Claude Code:

    /publish-news inbox/lago-sip-2026

Images arriving later? Add them to the folder and run the same command again.
See ../../NEWS-WORKFLOW.md (outside the repo) for the whole workflow.
