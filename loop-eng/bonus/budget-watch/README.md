# Budget Watch — a loop that knows its own limit

**Bonus project — bounded loops (self-limiting, not just self-scheduling).**

Every scheduled loop in this course ([Sky Watch](../../sky-watch/), [Paper Watch](../../paper-watch/))
assumes it can call its API whenever the clock says to. Real APIs push back: GitHub's public,
unauthenticated REST API allows exactly **60 requests per hour, per IP address** — and hands back
your remaining balance with every call. This project watches that balance, live.

## Run it

```bash
git clone https://github.com/panaversity/agentfactory-labs.git
cd agentfactory-labs/crash-course/loop-eng/bonus/budget-watch
claude
```

Say **yes** when Claude asks whether you trust the folder. Then ask:

```
how much of my GitHub API budget is left?
```

```
  💳  GITHUB API BUDGET   (unauthenticated, per IP address)
  ------------------------------------------------------------
     [██████████████████████████████████████░░░░░░]  53/60 left  (88%)
     Resets       15:32:07 local time
     This check spent 1 of those 60 -- checking is not free.
  ------------------------------------------------------------
```

Run it again right away and watch the number go down by exactly one — that is not drift, that is
this very check spending its own subject.

## Feel the self-reference

Ask a handful of times in a row:

```
check my API budget again
```

Each check costs one request out of the 60 it is reporting on. Do this ~50 times in an hour (easy
in a live demo — just keep asking) and it flips to a warning:

```
     ⚠ below 20% -- a scheduled loop should back off now, not keep polling.
```

That is the lesson: **a loop that measures a resource by consuming it needs to count its own
measurements**, or its "how much is left?" checks are quietly eating the very thing they watch.

## How this differs from the other scheduled watches

Sky Watch and Paper Watch both run on a **daily clock** and never think about budget — NASA's demo
key and arXiv's open API are generous enough that it never comes up. This project is the other
half of that story: a loop that must track a **hard, finite ceiling** and change its own behaviour
— slow down, or stop — as it approaches it, instead of finding out by crashing into a 403 at 3am.

| Heartbeat kind | What limits it | What happens at the limit |
|---|---|---|
| Sky Watch / Paper Watch | the clock (once a day) | nothing — the API has headroom to spare |
| **Budget Watch (this)** | **a hard request quota** | **the loop must warn or stop itself, on purpose** |

## What it ships

| File                                              | Job                                                                |
| -------------------------------------------------- | ------------------------------------------------------------------- |
| `.claude/skills/budget-watch/`                     | Owns the fetch and the warn-threshold decision                      |
| `.claude/skills/budget-watch/scripts/budgetwatch.py` | Calls GitHub's real rate-limit endpoint; never guesses a number   |
| `.claude/settings.json`                            | Three narrow pre-granted rules: the skill, the script, `api.github.com` |
| `AGENTS.md`                                        | Points any agent at the skill/script — read by every agent          |
| `CLAUDE.md`                                        | One line — imports `AGENTS.md` so Claude Code reads it too          |

## Try pairing it with a schedule

```
/schedule every 15 minutes, check the API budget and only message me if it's below 20%
```

Silent while there's headroom, loud only when the loop is close to its own limit — the same
"quiet on the quiet days" shape as Sky Watch, applied to a resource instead of a sky.
