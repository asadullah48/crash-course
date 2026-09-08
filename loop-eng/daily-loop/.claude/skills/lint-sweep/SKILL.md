---
name: lint-sweep
description: Run the daily lint sweep across this repo's own loop-eng projects (never the course-provided starter kits) -- isolate the work in a worktree, run the bundled maker-checker script, and open a PR only if it found and fixed real issues. Use whenever asked to run today's lint sweep, or on the daily schedule that drives Project 8's unattended loop.
---

# Lint Sweep — Project 8's daily chore

One job, once a day: keep our own `loop-eng/` projects (listed in `scope.txt`, never
the original course starter kits) ruff-clean, with no PR opened unless there was a
real, checker-confirmed fix to ship.

**This skill has six steps. The script only owns two of them (maker + checker +
spine-writing) — worktree, spine persistence, and connector are this skill's job,
not the script's.**

## Step 1 — Worktree: isolate today's beat

Never edit the main checkout directly. Create a fresh, disposable worktree:

```bash
DATE=$(date -u +%Y-%m-%d)
git worktree add "../crash-course-lint-sweep-$DATE" -b "claude/lint-sweep-$DATE" main
cd "../crash-course-lint-sweep-$DATE"
```

If a worktree/branch for today already exists (the beat already ran once today),
that's not an error — reuse it, or skip straight to step 2 there.

## Step 2 — Restore the spine before running

**A fresh clone never contains yesterday's `progress.md` on its own.** The spine
lives on a dedicated, never-merged branch, `claude/daily-loop-spine`, because this
loop's standing permission is "push to `claude/*`," never "push to `main`" — and the
spine is pure runtime log data, not code, so it does not belong in a PR reviewed
alongside real fixes. Before running the script, pull that branch's copies of
`progress.md` and `loop.log` into the worktree so `read_spine()` actually sees prior
history:

```bash
git fetch origin claude/daily-loop-spine 2>/dev/null
git show origin/claude/daily-loop-spine:loop-eng/daily-loop/progress.md \
  > loop-eng/daily-loop/progress.md 2>/dev/null || true
git show origin/claude/daily-loop-spine:loop-eng/daily-loop/loop.log \
  > loop-eng/daily-loop/loop.log 2>/dev/null || true
```

On the very first run ever, `claude/daily-loop-spine` does not exist yet — both
`git show` calls fail silently (`|| true`), and the script starts both files fresh,
exactly as before.

## Step 3 — Run the script (maker + checker + spine, in one call)

```bash
python3 loop-eng/daily-loop/.claude/skills/lint-sweep/scripts/lint_sweep.py
```

Read its exit code. **Do not re-run ruff yourself, do not second-guess the checker's
verdict** — the script already ran a real maker pass and a real, separate checker
pass; that separation is the whole point (Concept 11).

| Exit code | What happened | What you do next |
| --- | --- | --- |
| `0` | Nothing to fix, all scoped dirs clean | Go to step 4 (persist the spine), then step 6 (clean up). No PR — a clean sweep is not news. |
| `2` | Found issues, fixed them, checker confirms clean | Go to step 4, then step 5 — open a PR. |
| `1` | Issues remain that ruff could not auto-fix, OR `scope.txt`/the issue count broke a safety cap | **Needs a human.** `progress.md` and `loop.log` already have the note (`mark_failure()` wrote it). Go to step 4 so that note actually survives, then step 6. Do not attempt to fix it yourself, do not open a PR with known issues in it — a human reads the note next.

## Step 4 — Persist the spine (every beat, every exit code)

This is the step that makes the spine real. Regardless of what happened in step 3,
commit and force-push `progress.md` and `loop.log` to the dedicated spine branch —
force, because this branch has exactly one writer (this loop) and always represents
"current spine content," not a reviewed history:

```bash
git add -f loop-eng/daily-loop/progress.md loop-eng/daily-loop/loop.log
git commit -m "Spine: beat for $DATE"
git push origin HEAD:claude/daily-loop-spine --force
```

If this step is ever skipped, the loop is back to the original bug: tomorrow's beat
restores nothing in step 2, and today's entry is gone forever.

## Step 5 — Connector: open a PR, only on exit code 2

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
permission is "open a PR," never "push to `main`" — a human still merges it. Note
this is a *second*, separate commit from step 4's spine push — code fixes go through
review on their own branch; the spine never does, because it isn't code.

## Step 6 — Clean up

```bash
cd -
git worktree remove "../crash-course-lint-sweep-$DATE" --force
```

(`--force` here only discards the *worktree checkout*, not history — every commit
from steps 4 and 5 is already pushed to `origin` by the time this runs.)

## The one thing to hold onto

`progress.md` (the spine — what the work found) and `loop.log` (the harness log — what
the system did, every beat) are both written by the script every single beat, success
or failure — but writing them locally is not the same as them surviving. This loop's
spine used to be gitignored, which meant it looked correct inside any one run (the
script really did write an entry) while silently losing that entry the moment the
session ended, because a gitignored file never leaves a cloud clone (A4) and the next
beat starts from nothing. Three real beats ran that way before it was caught: each one
only ever saw its own single entry. Steps 2 and 4 exist specifically to close that gap
— restore the spine before running, persist it after, every beat, no exceptions. If
either file is ever missing an entry for a day the loop should have run, *that* gap is
the finding now — see `loop-eng/break-it-on-purpose/` for why a missing log line is
worse than any single failed beat, and see `loop-eng/dreaming-loop/` for the loop built
specifically to notice this kind of repeated pattern instead of a human having to.
