---
name: lint-sweep
description: Run the daily lint sweep across this repo's own loop-eng projects (never the course-provided starter kits) -- isolate the work in a worktree, run the bundled maker-checker script, and open a PR only if it found and fixed real issues. Use whenever asked to run today's lint sweep, or on the daily schedule that drives Project 8's unattended loop.
---

# Lint Sweep — Project 8's daily chore

One job, once a day: keep our own `loop-eng/` projects (listed in `scope.txt`, never
the original course starter kits) ruff-clean, with no PR opened unless there was a
real, checker-confirmed fix to ship.

**This skill has four steps. The script only owns two of them (maker + checker +
spine) — worktree and connector are this skill's job, not the script's.**

## Step 1 — Worktree: isolate today's beat

Never edit the main checkout directly. Create a fresh, disposable worktree:

```bash
DATE=$(date -u +%Y-%m-%d)
git worktree add "../crash-course-lint-sweep-$DATE" -b "claude/lint-sweep-$DATE" main
cd "../crash-course-lint-sweep-$DATE"
```

If a worktree/branch for today already exists (the beat already ran once today),
that's not an error — reuse it, or skip straight to step 2 there.

## Step 2 — Run the script (maker + checker + spine, in one call)

```bash
python3 loop-eng/daily-loop/.claude/skills/lint-sweep/scripts/lint_sweep.py
```

Read its exit code. **Do not re-run ruff yourself, do not second-guess the checker's
verdict** — the script already ran a real maker pass and a real, separate checker
pass; that separation is the whole point (Concept 11).

| Exit code | What happened | What you do next |
| --- | --- | --- |
| `0` | Nothing to fix, all scoped dirs clean | Nothing. Remove the worktree (step 4) and stop. No PR — a clean sweep is not news. |
| `2` | Found issues, fixed them, checker confirms clean | Go to step 3 — open a PR. |
| `1` | Issues remain that ruff could not auto-fix, OR `scope.txt`/the issue count broke a safety cap | **Needs a human.** `progress.md` and `loop.log` already have the note (`mark_failure()` wrote it). Do not attempt to fix it yourself, do not open a PR with known issues in it. Remove the worktree (step 4) and stop — a human reads the note next.

## Step 3 — Connector: open a PR, only on exit code 2

```bash
git add -A
git commit -m "Lint sweep: fix N issue(s) across the scoped projects

$(cat loop-eng/daily-loop/progress.md | tail -20)"
git push -u origin "claude/lint-sweep-$DATE"
gh pr create --base main --head "claude/lint-sweep-$DATE" \
  --title "Daily lint sweep: $DATE" \
  --body "Ruff-clean fixes only, checker-confirmed. See loop-eng/daily-loop/progress.md for this beat's entry. Opened by the scheduled lint-sweep loop, not a person."
```

The `claude/` branch prefix is deliberate (Concept 14): this loop's standing
permission is "open a PR," never "push to `main`" — a human still merges it.

## Step 4 — Clean up

```bash
cd -
git worktree remove "../crash-course-lint-sweep-$DATE" --force
```

(`--force` here only discards the *worktree checkout*, not history — the branch and
its commit are already pushed to `origin` by step 3, or nothing was committed at all
on exit codes 0/1.)

## The one thing to hold onto

`progress.md` (the spine — what the work found) and `loop.log` (the harness log — what
the system did, every beat) are both written by the script, every single beat, success
or failure. If either file is ever missing an entry for a day the loop should have run,
that gap is itself the finding — see `loop-eng/break-it-on-purpose/` for why a missing
log line is worse than any single failed beat.
