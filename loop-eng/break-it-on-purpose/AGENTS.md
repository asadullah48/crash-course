# Morning Brief

This project has one job: once a run, write a short brief of what changed in the repo,
and remember where it left off so the next run does not repeat itself.

**Any request for the brief is answered by running this project's script, never from
memory or by re-deriving history yourself:**

    python3 .claude/skills/morning-brief/scripts/brief.py

(In Claude Code this runs automatically through the `morning-brief` skill; any other
agent should run the script directly.) The script owns the spine: it reads
`progress.md` first to find the last commit it reported on, gathers only commits and
TODO/FIXME counts since then, and writes `progress.md` last with a fresh entry and an
updated bookmark.

The one thing to hold onto: this loop has a **memory**. `progress.md` is the spine.
Reading it first is what lets each run report only what's new instead of repeating
yesterday's findings. Delete `progress.md` and the loop forgets everything -- the next
run treats the whole repo history as a first-time baseline. **No spine, no loop.**
