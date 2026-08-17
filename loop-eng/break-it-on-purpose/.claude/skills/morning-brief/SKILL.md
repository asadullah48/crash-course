---
name: morning-brief
description: Write today's morning brief -- commits since the last run and open TODO/FIXME comments -- by running this skill's bundled script, never by guessing what changed. The script reads progress.md (the spine) first so it reports only what's new, and writes progress.md last. Use whenever the user asks for the morning brief, wants a daily repo summary, or runs a scheduled "what happened since yesterday" job.
---

# Morning Brief

This project has one job: once a run, write a short brief of what changed in the repo,
and remember where it left off so the next run does not repeat itself.

**Any request for the brief is answered by running this project's script, never from
memory or by re-deriving history yourself:**

    python3 .claude/skills/morning-brief/scripts/brief.py

The script owns the spine: it reads `progress.md` first to find the last commit it
reported on, gathers only commits and TODO/FIXME counts since then, and writes
`progress.md` last with a fresh entry and an updated bookmark. If `sources.md` lists
extra files, it folds those in too -- and if one of those listed files is missing, the
script does not skip it quietly: it stops, and leaves a note in both `loop.log` and
`progress.md` saying so.

The one thing to hold onto: this loop has a **memory**. `progress.md` is the spine.
Reading it first is what lets each run report only what's new instead of repeating
yesterday's findings. Delete `progress.md` and the loop forgets everything -- the next
run treats the whole repo history as a first-time baseline. **No spine, no loop.**

If the run ever fails, `loop.log` is the first place to look -- one line per beat, every
beat, saying whether it finished clean or needs a human. Read that before re-running
anything.
