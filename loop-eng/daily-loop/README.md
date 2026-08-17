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

<!-- filled in after the routine is created and test-fired -->

## Status

<!-- filled in after landing on main and the first real fire -->
