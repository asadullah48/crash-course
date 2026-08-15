---
name: budget-watch
description: Check the real, live GitHub API rate-limit budget by running this skill's bundled script -- never from memory or a guessed percentage. Use it whenever the user asks how much API budget is left, wants to check a rate limit, asks whether a loop is about to run out of quota, or wants to see a loop that stops itself before hitting a hard limit. The script owns the fetch and the warn-threshold decision -- report its numbers exactly, including that the check itself spent one unit of budget.
allowed-tools: Bash, Read
---

# Budget watch

Most loops in this course assume the thing they call is free to call as often as they like. It
usually is not. GitHub's public, unauthenticated API allows exactly 60 requests per hour per IP
address, and hands back the remaining balance with every response. This skill checks that balance
-- and spends one of the 60 requests doing so, which is the whole point: **checking a budget is
not free, and a loop that forgets that runs out faster than it thinks.**

## Checking the budget

```bash
python3 .claude/skills/budget-watch/scripts/budgetwatch.py
```

Prints a bar showing remaining/limit, when it resets, and a reminder that the check itself cost
one unit. Exit code doubles as a signal a real scheduled loop could act on:

- `0` — plenty of budget left.
- `2` — under the warning threshold (default 20%). A scheduled loop should read this as "back off,"
  not "keep polling at the same rate."
- `1` — the fetch itself failed. Never invent a budget number; say the check failed.

## Why this matters for a scheduled loop

[Sky Watch](../../sky-watch/) runs once a day and never worries about budget, because NASA's demo
key is generous. Not every API is. A loop meant to run unattended for weeks needs to know its own
limit and slow down -- or stop -- before it hits it, rather than finding out from an error message
at 3am. That is a **bounded loop**: it treats a finite resource as part of its own stop condition,
not something to discover by crashing into it.
