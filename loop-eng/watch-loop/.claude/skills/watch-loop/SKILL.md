---
name: watch-loop
description: Start the long-running background task or check whether it has finished, by running this skill's bundled scripts -- never by guessing elapsed time. Use whenever the user asks to start the watch-loop task, check if it's done, or wants a loop that waits for it and reports once.
---

# Watch Loop

This project has one job: run a long task in the background, and watch for it to finish
without anyone sitting and staring at the terminal.

**Starting the task** (do this once, in the background so the session stays free):

    python3 .claude/skills/watch-loop/scripts/long_task.py --seconds 90

**Checking whether it's done** — never guess based on how much time has "probably" passed;
always run the checker, because the real answer lives in `.task/status.json`, not in your head:

    python3 .claude/skills/watch-loop/scripts/check_status.py

Exit code `0` means done, `1` means still running or not started. A watch loop should poll this
on a cadence (once a minute is the point of this project) and stop the instant it sees `0` --
report completion exactly once, then end the loop. Don't re-run the checker in a tight spin loop;
that defeats the purpose of a heartbeat-based watch.
