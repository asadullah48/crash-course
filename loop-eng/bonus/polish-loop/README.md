# Polish Loop — a loop that doesn't grade its own homework

**Bonus project — self-review loops (generator + critic).**

Ask an agent to write something and then ask *the same agent* whether it's good, and it will
almost always say yes — it already committed to the answer once. A self-review loop only works if
the thing that judges "done" is not the same judgment as the thing that wrote it. This project
splits the two apart: you (with Claude) write, and a small fixed script — with no opinion to
flatter — grades.

## Run it

```bash
git clone https://github.com/panaversity/agentfactory-labs.git
cd agentfactory-labs/crash-course/loop-eng/bonus/polish-loop
claude
```

Say **yes** when Claude asks whether you trust the folder. Read `brief.md`, then ask:

```
write me a 30-second elevator pitch about myself and get it passing the critic
```

Watch the loop happen out loud — write, grade, read what failed, revise, grade again:

```
  pitch.md
  [x] C1  length 60-90 words (~30s spoken)   -> 74 words
  [ ] C2  no banned buzzwords                 -> passionate about, cutting-edge
  [x] C3  opens with a hook, not a greeting   -> ok
  [x] C4  includes one concrete number or fact -> ok
  [ ] C5  ends with a clear ask                -> last sentence: "Thanks for listening."

  3/5 passing
```

It rewrites, cutting the buzzwords and swapping the closing line for an actual ask, then re-runs
the critic — until every line has an `x` and it prints `5/5 passing`.

## The rule that makes this a *loop* and not just editing

**Only `critic.py` gets to say PASS.** An agent asked "is this pitch good?" will reliably find a
reason to say yes — that is not malice, it is what happens when the writer and the judge are the
same process. This project makes the judge a different thing entirely: a script with five checks,
none of them negotiable, none of them moved by a persuasive rewrite that dodges the letter of the
rule. "Never edit the checker to make it pass" is not a suggestion here — it is the same rule
[Build Your Portfolio](../../portfolio-starter/)'s `check.py` lives by, at a fifth of the size.

## How this differs from every other loop here

Every heartbeat so far — schedule, event, in-session — decides **when** to run. This one is about
what happens **inside** a single run: not "run again later," but "revise right now, based on
specific, itemized feedback, until a fixed bar is cleared." A pitch that passes on attempt 1 never
gets a second look; a pitch that fails 4 times gets rewritten 4 times. The loop's length is decided
by the work, not the clock.

## What it ships

| File                                              | Job                                                                  |
| --------------------------------------------------- | ----------------------------------------------------------------------- |
| `brief.md`                                          | The assignment — what to write, and what the critic will check          |
| `.claude/skills/polish-loop/`                       | Owns the write/grade/revise loop and the "never edit the critic" rule   |
| `.claude/skills/polish-loop/scripts/critic.py`      | The critic — five fixed checks, Python stdlib only, no opinions         |
| `.claude/settings.json`                             | Narrow pre-granted rules: the skill and the script — no network needed  |
| `AGENTS.md`                                         | Points any agent at the skill/script — read by every agent              |
| `CLAUDE.md`                                         | One line — imports `AGENTS.md` so Claude Code reads it too              |

## Requirements

Python 3 only. No network, no API key, no npm — the critic reads a text file and counts things in it.
