# A Watch Loop

This project has one job: start a long-running task in the background, then watch for it
to finish without anyone sitting at the terminal.

**Starting the task, and checking whether it is done, are both answered by running this
project's scripts -- never by guessing elapsed time or narrating a simulated wait:**

    python3 .claude/skills/watch-loop/scripts/long_task.py --seconds 90
    python3 .claude/skills/watch-loop/scripts/check_status.py

(In Claude Code this runs automatically through the `watch-loop` skill; any other agent
should run the scripts directly.) `long_task.py` owns the work and the completion write;
`check_status.py` owns the read. Neither is guessed.

The one thing worth stating up front: the checker's exit code (`0` = done, `1` = not yet)
is the only source of truth. A loop watching this task should poll on a cadence (once a
minute), stop polling the instant it sees `0`, and announce completion exactly once --
not on every poll.
