# dreaming-state.md — the dreaming loop's own memory

Records the latest daily-loop `progress.md`/`loop.log` entry date this loop has
already processed, so the next weekly run only looks at what's new.

## Last processed

**2026-08-17 19:41 UTC** — the last entry present in `loop-eng/daily-loop/progress.md`
and `loop-eng/daily-loop/loop.log` on `claude/daily-loop-spine` as of this run.

## Run history

### 2026-08-17

- First run — no prior `dreaming-state.md` existed, so the full history in
  `progress.md`/`loop.log` on `claude/daily-loop-spine` was considered (entries
  2026-08-11 03:04 UTC through 2026-08-17 19:41 UTC).
- Found a repeated failure: `F841` at
  `loop-eng/break-it-on-purpose/.claude/skills/morning-brief/scripts/brief.py:52`,
  identical in the 2026-08-13 03:06 UTC and 2026-08-16 03:04 UTC FAILED entries.
- Proposed fix (see PR): scope a `ruff.toml` to the lint-sweep skill's own ruff
  calls, promoting `F841`'s fix from "unsafe" to "safe" via `extend-safe-fixes`,
  so the maker can actually clear a trivial unused-variable case instead of
  always deferring to a human.
- Also flagged one settings.json permission suggestion (see PR body) — not
  applied directly, per the harness guardrail on unattended `.claude/settings.json`
  writes.
