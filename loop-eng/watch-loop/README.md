# A Watch Loop

**Loop Engineering, Concept 4 — in-session loops (repeat while you watch).**

A background task runs on its own clock. A loop checks on it once a minute, says nothing
while it is still going, and speaks up exactly once the moment it is done. You never sit
and stare at a spinner.

## Run it

```bash
cd loop-eng/watch-loop
claude
```

Say **yes** when Claude asks whether you trust this folder. Then type:

```
start the long task, then watch for it to finish and tell me once
```

What happens:

1. `long_task.py` starts in the background (default: finishes in 90 seconds) and immediately
   writes `.task/status.json` with `"status": "running"`.
2. A loop begins polling `check_status.py` once a minute.
3. The moment the exit code says "done," the loop reports it — once — and stops. No further
   polling, no repeated messages.

Say `stop the watch loop` (or just close the session) any time before it finishes and the
watching ends immediately with nothing left running.

## Why this is different from watching the ISS

The [ISS project](../iss-loop/) polls forever and reports **every** minute — that loop has
no finish line, so "keep going" is correct. This one polls **until** a condition is true,
then reports **once** and stops — the finish line is the entire point.

That is the difference between a loop that repeats and a loop that terminates: both run on
the same one-minute heartbeat, but only one of them knows how to stop itself.

## What it ships

| File | Job |
| --- | --- |
| `.claude/skills/watch-loop/scripts/long_task.py` | The task. Sleeps, then writes `.task/status.json` atomically. |
| `.claude/skills/watch-loop/scripts/check_status.py` | The check. Exit code `0` = done, `1` = not yet. |
| `.claude/skills/watch-loop/` | Owns both scripts — never guess elapsed time instead of running the checker. |
| `.claude/settings.json` | Pre-granted rules so the loop never stops to ask permission each minute. |
| `AGENTS.md` / `CLAUDE.md` | Point any agent at the skill/scripts. |

## The one thing to notice

`check_status.py`'s exit code is the only thing the loop trusts — never "it's probably done
by now." A watch loop that estimates instead of checking is a guess wearing a stopwatch.
