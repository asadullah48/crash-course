# Your Own Daily Loop

**Loop Engineering — the capstone. Uses all six parts.**

> **Build.** Pick one real, boring, recurring chore in a project you actually work on:
> a dependency audit, a docs-freshness check, a changelog draft, a lint sweep. Build the
> full loop: heartbeat, worktree, skill, maker-checker, connector, and the spine. Add
> budget guards. Let it run.
>
> **Done when** it has run unattended for a week and you trust what it ships *because
> you read it*, not because you stopped reading. Then answer Concept 15 honestly: did
> your understanding of the project keep up with what the loop changed? If not, slow the
> loop down until it does. (When it fails overnight, and it will, work through
> [When an unattended loop fails](#observability) before you blame the model.)
>
> — [Loop Engineering: A Crash Course, Project 8](https://agentfactory.panaversity.org/docs/loop-engineering-crash-course#practice-projects)

**Status: heartbeat just switched on. The "ran unattended for a week" criterion is
NOT YET true and won't be claimed until it actually is** — see [Status](#status) at the
bottom for exactly what's been verified so far versus what's still pending real elapsed
time. Everything above that line already happened for real.

## The chore

**A lint sweep** across this repo's own `loop-eng/` projects, using [ruff](https://docs.astral.sh/ruff/)
— already the established tool here (`morning-brief` shipped with a `.ruff_cache/`).
Deliberately scoped to an **allowlist** (`scope.txt`), not "everything under
`loop-eng/`": the original course-provided starter kits (`iss-loop`, `sky-watch`,
`portfolio-starter`, `paper-watch`, `doorbell`, `bonus/*`) are not ours to
auto-reformat — only the projects we actually authored this course are in scope.

## The six parts

| Part | Where it lives | What it actually does |
| --- | --- | --- |
| **Heartbeat** | A daily cloud routine (see [Heartbeat](#heartbeat) below) | Starts a fresh, unattended cloud agent once a day. |
| **Worktree** | `SKILL.md` step 1 | `git worktree add ../crash-course-lint-sweep-$DATE -b claude/lint-sweep-$DATE main` — never edits the main checkout directly. |
| **Skill** | `.claude/skills/lint-sweep/SKILL.md` | The four-step orchestration: worktree → run the script → branch on its exit code → clean up. |
| **Maker-checker** | `lint_sweep.py`'s `run_maker()` / `run_checker()` | Maker: `ruff check --fix`. Checker: a **separate**, fresh `ruff check` with no `--fix` — the maker never grades its own work (Concept 11). |
| **Connector** | `SKILL.md` step 3 | `gh pr create`, only on the checker's exit code `2` (fixed and clean). Never pushes to `main` directly — a human still merges. |
| **Spine** | `progress.md` + `loop.log` | Identical contract to [break-it-on-purpose](../break-it-on-purpose/)'s `brief.py`: `progress.md` is what the *work* found, `loop.log` is what the *system* did, both written every beat, success or failure. |

## Budget guards

**Blast-radius cap, not just a token cap:** `lint_sweep.py` refuses to auto-fix
anything if a beat finds more than `MAX_ISSUES = 50` issues — a count that high almost
certainly means `scope.txt` grew unexpectedly or something unusual landed, and that's a
human's call, not the loop's (Concept 5: always cap a loop). It's a `mark_failure()`
case: `NEEDS HUMAN`, nothing touched.

**Token cost, estimated the same way as Project 7** (a real `claude -p` measurement was
blocked there by a zero API credit balance on this local environment — the cloud
routine below runs under the claude.ai subscription instead, a different auth path, so
that specific blocker doesn't apply to it, but a live per-beat reading still isn't
available from outside a run, so this is still an estimate, sized from the real files
here: `AGENTS.md` 1,247 bytes ≈ 310 tokens, `SKILL.md` 3,654 bytes ≈ 915 tokens):

| Day type | Extra tool round-trips | Est. input | Est. output | Est. cost |
| --- | --- | --- | --- | --- |
| Clean (exit 0) — worktree add, run script, remove worktree | ~3 | ~5,000 tok | ~150 tok | ~$0.017 |
| Fix + PR (exit 2) — + git add/commit/push, `gh pr create` | ~7 | ~8,000 tok | ~400 tok | ~$0.030 |

```
30 beats/month × $0.017 (all-clean)  ≈ $0.51/month
30 beats/month × $0.030 (all-fix)    ≈ $0.90/month
```

**Acceptable-limits check:** both bounds are comfortably under $1/month — cheap enough
that the loop's real cost driver isn't tokens, it's *trust* (Concept 15), which is what
the week-long unattended run is actually testing.

## Heartbeat

A real Claude Code cloud routine (`RemoteTrigger`/`/schedule`, not a local cron job):

- **Name:** `daily-lint-sweep`, id `trig_01BJm6f8soS7KLid6LiPREAc`
- **Schedule:** `0 3 * * *` UTC = **8:00am Asia/Karachi, every day**
- **Repo:** `https://github.com/asadullah48/crash-course` (cloned fresh each beat — the
  routine has no access to this local machine, only what's on GitHub)
- **Prompt:** self-contained (the cloud agent starts with zero context each beat) —
  points it at `SKILL.md`, tells it to follow the four steps exactly, and trust the
  script's exit code as the final verdict rather than re-judging the work itself.

## Status

**As of 2026-08-17, ~09:37 UTC — verified, not assumed:**

Test-fired the routine twice (`action: "run"`) to prove the mechanism actually works,
before trusting the schedule to fire it unattended:

**Fire 1** (`cse_01F4PJP33wusWfhCg9Wr9KjZ`) — **found a real bug**, not a planted one:
`scope.txt` listed `loop-eng/break-it-on-purpose`, but that project's own PR (#7)
hadn't been merged to `main` yet when this routine was created. The loop caught it
exactly as designed: `lint_sweep.py` exited 1, wrote a `NEEDS HUMAN` note to both
`progress.md` and `loop.log`, and the agent — per the skill — made no manual fix,
opened no PR, cleanly removed the worktree, and **sent a real push notification**:
*"Lint-sweep beat FAILED — scope.txt references a missing directory, needs a human.
No PR opened."* This is Concept 14 working exactly as intended, on a mistake that
was actually mine, not staged.

**Fixed the real cause**, not the symptom: merged PR #7 to `main` (after resolving one
merge conflict in `loop-eng/.gitignore` from two branches independently adding the same
line — a `daily-loop`-scope issue in its own right, now resolved).

**Fire 2** (`cse_01NrXeCxqkhScr4AKE1sDBE8`) — clean recovery, exit 0, all 4 scoped
directories ruff-clean, no PR, no notification, worktree removed. No code change was
needed — only what the note actually asked for.

**What this proves:** the heartbeat fires, clones from GitHub (not local disk), reads
the skill, creates and removes worktrees correctly, the maker-checker split holds, the
spine and harness log both work under a real failure, and the connector step is
correctly gated on exit code 2 (never fired in either test, correctly, since neither
beat found real fixable issues).

**What this does NOT yet prove, and is not being claimed:**

| Done-when criterion | Status |
| --- | --- |
| Run unattended for a week | ❌ **Not yet.** Two manually-triggered test-fires ≠ a week of the schedule firing on its own. First real scheduled fire: **2026-08-18, ~03:00 UTC**. Check back after **2026-08-24** — `RemoteTrigger action: "list_runs"` on `trig_01BJm6f8soS7KLid6LiPREAc`, or `cat loop-eng/daily-loop/progress.md` after a `git pull`, should show ~7 daily entries with no scheduling gaps. |
| Trust what it ships because you read it | Partial — the two test-fires were read in full above. A week of real diffs, read the same way, is what this line actually asks for. |
| Concept 15 — did understanding keep up? | Honest answer so far: **yes, because the first real fire forced it to** — the missing-directory bug surfaced a real gap between what `scope.txt` claimed and what was actually merged, and closing that gap required reading the failure, not just green-lighting it. |
| Slow the loop down if not | Not triggered — daily is working so far. If a week of real fires shows drift, switch `daily-lint-sweep`'s cron to weekly via `RemoteTrigger action: "update"`. |
