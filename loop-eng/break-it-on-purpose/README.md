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
