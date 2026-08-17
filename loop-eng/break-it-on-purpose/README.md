# Break It on Purpose

**Loop Engineering — [Observability](https://agentfactory.panaversity.org/docs/loop-engineering-crash-course#observability), Concept 13 (token cost), Concept 14 (checking the work is still your job).**

> **Build.** Take your Project 3 loop. First, measure one beat: note roughly how many
> tokens a run reads and writes, and multiply by your cadence to get a monthly cost,
> which is Concept 13's math on your own loop. Then sabotage it: point the prompt at a
> file that does not exist, or give it a success condition it can never meet (with a
> limit set). Let it fire on schedule and fail. Now diagnose the failure using only what
> the loop left behind, meaning the log line and `progress.md`, without replaying the
> full run.
>
> **Done when** three things are true. You can say what failed, and when, from the
> spine alone. The loop left a clear "needs a human" note instead of failing silently.
> And you know your loop's monthly cost at its current cadence. If it failed silently,
> fix that before anything else by adding the log line. You are rehearsing the overnight
> failure now, while it is cheap and you are watching.
>
> — [Loop Engineering: A Crash Course, Project 7](https://agentfactory.panaversity.org/docs/loop-engineering-crash-course#practice-projects)

This is a rehearsal, not a demo. Everything below actually ran; nothing is narrated as if
it happened. Where a step failed, the failure and its exact output are shown, not
summarized away.

## Step 1 — Take Project 3's loop, unmodified

Everything in `.claude/skills/morning-brief/` and `AGENTS.md`/`CLAUDE.md`/
`.claude/settings.json` here is a byte-for-byte copy of the
[morning-brief](../morning-brief/) project — the scheduled loop with a spine from
Project 3. Nothing about the loop itself changes until Step 3.

Run it once to set the baseline:

```
$ python .claude/skills/morning-brief/scripts/brief.py

  🌅  MORNING BRIEF  ·  2026-08-17 08:19 UTC
      first run — establishing a baseline, nothing to compare against yet
  ------------------------------------------------------------
   open TODO/FIXME comments right now: 0
  ------------------------------------------------------------
   saved this to progress.md, so tomorrow's run remembers it.
```

## Step 2 — Measure one beat (Concept 13's math, on this loop)

**Attempted a real measurement first.** This project's own `claude -p "give me this
morning's brief" --output-format json` was actually run to pull real usage numbers
straight from a live beat. It returned immediately with `"result":"Credit balance is
too low"` and `total_cost_usd: 0` — no tokens were spent, but no real measurement came
back either. So the numbers below are a grounded *estimate*, not a live reading, exactly
as the project brief allows ("note *roughly* how many tokens a run reads and writes").

**What actually gets read, every beat**, sized from the real files in this project (not
guessed):

| Piece | Size | ≈ tokens (÷4 chars) |
| --- | --- | --- |
| `AGENTS.md` (loaded via `CLAUDE.md`'s `@AGENTS.md` import, every session) | 1,053 bytes | ~260 |
| `SKILL.md` (loaded when the `morning-brief` skill triggers, every beat) | 1,375 bytes | ~340 |
| `brief.py`'s printed output (the Bash tool result Claude reads back) | 325 bytes | ~80 |
| Claude Code's own baseline system prompt + tool schemas (not directly measurable from outside a live session; this project's `settings.json` narrows what's *allowed*, not what's *declared*, so this cost is paid regardless) | — | ~3,000 (order-of-magnitude, industry-typical for a minimal-tool session) |
| **Total input, one beat** | | **≈ 4,000 tokens** |

**What gets written:** one short natural-language reply summarizing the brief for the
user — a few sentences, **≈ 200 tokens**. (`progress.md` itself is written directly by
the Python script, not by the model, so it costs no output tokens.)

**Cost per beat**, at Sonnet's standard price ($3 / M input, $15 / M output — see
[Concept 13](https://agentfactory.panaversity.org/docs/loop-engineering-crash-course#13-token-cost)):

```
input:  4,000 / 1,000,000 × $3  = $0.012
output:   200 / 1,000,000 × $15 = $0.003
                                  --------
                            ≈    $0.015 / beat
```

**Cadence, from this loop's own README:** `/schedule every morning at 8am` — once a
day, so **≈ 30 beats/month**.

```
$0.015/beat × 30 beats/month ≈ $0.45/month
```

That's cheap, and by design: this loop has no subagents, fires once a day (not every
few minutes), keeps its prompt and skill short, and pushes the actual work into a
deterministic Python script instead of paying LLM tokens to re-derive `git log` output
every time. Concept 13's warning example (a maker+checker beat, every five minutes) hits
over $1,800/month; this loop is roughly **4,000× cheaper**, purely from cadence and
shape — the same lever the course names as the biggest one.

## Step 3 — Sabotage it: point the prompt at a file that does not exist

Added one small feature to `brief.py`: an optional `sources.md` lets the brief fold in
extra files. Then `sources.md` was pointed at `docs/release-highlights.md` — a file that
was never created:

```
$ cat sources.md
docs/release-highlights.md
```

No safety net was added around this yet — a realistic first cut, the kind a real edit
would actually ship.

## Step 4 — Let it fire on schedule and fail

```
$ python .claude/skills/morning-brief/scripts/brief.py

Traceback (most recent call last):
  File ".../brief.py", line 191, in <module>
    main()
  File ".../brief.py", line 166, in main
    sources = read_sources()
  File ".../brief.py", line 121, in read_sources
    return [(path, open(path, encoding="utf-8").read().strip()) for path in paths]
FileNotFoundError: [Errno 2] No such file or directory: 'docs/release-highlights.md'

EXIT CODE: 1
```

It failed, loudly, in the terminal. But an `/schedule every morning at 8am` run has no
one watching that terminal. So the real question is: **what does this look like from
the spine, the next morning?**

```
$ cat progress.md
...
## 2026-08-17 08:19 UTC

New commits since last run: none.
Open TODO/FIXME comments in repo: 0

$ cat loop.log
cat: loop.log: No such file or directory
```

**Nothing.** `progress.md`'s last entry is indistinguishable from a normal clean run —
it was written by the *previous*, successful beat, and the crashed beat never got far
enough to touch it. `loop.log` doesn't exist at all. Read only the spine, as the
project's own rule requires, and this beat's failure is **invisible**. That is the
silent failure this project exists to catch: loud in a terminal nobody was watching,
silent in the only record that survives until morning.

## Step 5 — Fix that first: add the log line

Two additions to `brief.py`, nothing else touched:

- **`log_beat(status, detail)`** — appends one line to `loop.log` every beat, success or
  failure. This is the *harness* log: what the **system** did. `progress.md` stays the
  *spine*: what the **work** found. Concept 14 turns on being able to tell those two
  apart — a loop that only ever writes the spine has no record of a beat that broke
  before it got far enough to write anything.
- **`mark_failure(reason)`** — on any `OSError` while gathering the brief (a missing
  `sources.md` file included), write the failure to *both* `loop.log` and `progress.md`,
  print a `🚨 NEEDS A HUMAN` banner, and exit non-zero. Two copies on purpose: whichever
  file a human opens first, they get the full picture.

Re-fired the exact same sabotaged case:

```
$ python .claude/skills/morning-brief/scripts/brief.py
  🚨  BEAT FAILED — NEEDS A HUMAN: could not finish gathering the brief: [Errno 2] No such file or directory: 'docs/release-highlights.md'

EXIT CODE: 1
```

**A real bug turned up here, and it's worth keeping in the record rather than editing
away.** The first attempt at that banner printed as `\U0001f6a8 BEAT FAILED � NEEDS...`
— garbled. The original script only reconfigured `sys.stdout` to UTF-8 for the emoji in
`show()`; `mark_failure()`'s banner prints to `sys.stderr`, which was still on Windows'
default `cp1252` and couldn't encode `🚨` or `—`. Fixed by reconfiguring both streams.
The underlying files (`loop.log`, `progress.md`) were unaffected the whole time — they're
opened with `encoding="utf-8"` explicitly — only the *console echo* of the failure note
was briefly unreadable. Small, but it's exactly the kind of thing this rehearsal is for:
better to find a broken "needs a human" note now than at 3am when it's the only thing
standing between a real failure and silence.

## Diagnose the failure — from the spine alone

Reading **only** `loop.log` and `progress.md`, no replay, no re-running anything:

```
$ cat loop.log
2026-08-17 08:27 UTC  status=FAILED  detail=could not finish gathering the brief: [Errno 2] No such file or directory: 'docs/release-highlights.md' — NEEDS HUMAN
2026-08-17 08:28 UTC  status=FAILED  detail=could not finish gathering the brief: [Errno 2] No such file or directory: 'docs/release-highlights.md' — NEEDS HUMAN

$ tail -8 progress.md
## 2026-08-17 08:27 UTC

**FAILED — NEEDS HUMAN.** could not finish gathering the brief: [Errno 2] No such file or directory: 'docs/release-highlights.md'

## 2026-08-17 08:28 UTC

**FAILED — NEEDS HUMAN.** could not finish gathering the brief: [Errno 2] No such file or directory: 'docs/release-highlights.md'
```

**What failed:** `sources.md` lists `docs/release-highlights.md` as a required extra
source, and that file doesn't exist — `read_sources()` raised `FileNotFoundError`
before the beat could finish.
**When:** first at `2026-08-17 08:27 UTC`, and again at `08:28 UTC` — two separate
beats, same cause, so it's not a one-off blip.
**What it needs:** exactly what both files say — `NEEDS HUMAN` — because a missing
promised file isn't something the loop can fix by retrying; a person has to either
create the file or remove it from `sources.md`.

## Recovery — a human acts on the note

```
$ cat > docs/release-highlights.md   # the human creates the missing file
$ python .claude/skills/morning-brief/scripts/brief.py

  🌅  MORNING BRIEF  ·  2026-08-17 08:29 UTC
      2 new commit(s) since last run
  ------------------------------------------------------------
   • edba811 Sabotage the loop: point sources.md at a file that does not exist
   • b557b8b Add break-it-on-purpose: Project 3's loop, unmodified
   open TODO/FIXME comments right now: 12
   + folded in extra context from docs/release-highlights.md
  ------------------------------------------------------------
   saved this to progress.md, so tomorrow's run remembers it.

EXIT CODE: 0
$ tail -1 loop.log
2026-08-17 08:29 UTC  status=OK  detail=2 commit(s), 12 TODOs
```

Clean exit, `status=OK` back in `loop.log`, extra source folded in as intended. The
loop didn't need code changes to recover — only the thing the note actually asked for.

## Done when — checked against the project's own criteria

| Criterion | Evidence |
| --- | --- |
| State what failed, and when, from the spine alone | Done above, reading only `loop.log` + `progress.md` — a missing `sources.md` entry, `08:27` and `08:28 UTC`. |
| The loop leaves a clear "needs a human" note instead of failing silently | `🚨 NEEDS A HUMAN` in both files, present tense, unmissable — **but only after Step 5.** Step 3-4's commit is the honest record of what "failing silently" actually looked like first. |
| Know the loop's monthly cost at its current cadence | **≈ $0.45/month** at the daily `/schedule` cadence (Step 2) — an estimate, clearly labeled, after a real measurement attempt was blocked by a zero API credit balance. |

Two commits capture the "if it failed silently, fix that first" arc as it actually
happened, not as a retelling: [`edba811`](https://github.com/asadullah48/crash-course/commit/edba811)
sabotages the loop with no safety net and shows the silence; the observability fix
lands on top of it, still on this branch, before any diagnosis was written up.

