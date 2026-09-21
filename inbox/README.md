# inbox/ - your input for news posts

This folder is how you hand material to the site agent. The agent never goes
looking for talks, posters or conferences: **if it is not in `inbox/`, no post
is made.** Everything here except this README and `_template/` is git-ignored,
so nothing you put here is committed or published - only the post that
`/draft-2-news` makes from it, once you commit that post.

    inbox/
      _template/brief.md       <- copy this
      zago-2026-sipf/          <- one folder per item: surname-year-event
        brief.md               <- template or plain text: who, what, where, when
        photo1.jpg             <- images, any names; the first is the thumbnail

Then, in Claude Code (session opened on the site repo):

    /draft-2-news inbox/zago-2026-sipf     # draft this one
    /draft-2-news                          # list folders with no post yet

The post goes to posts/news-title/ (About -> News) as a draft. Images arriving
later? Add them to the folder and run `/draft-2-news inbox/<slug>` again - the
same post is updated.

Posts about papers come from `publications.xlsx` via `/pub-2-news`; an inbox
folder named after the paper can add extra text or a figure to that post.

Full workflow: ../.claude/WORKFLOW.md
