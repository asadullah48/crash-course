# Daily Loop — lint sweep

This project has one job, once a day: sweep the repo's own `loop-eng/` projects
(listed in `scope.txt`) for lint issues, fix what a real checker confirms is fixable,
and open a PR only when there's a real, checker-confirmed fix to ship.

**Any request to run today's sweep is answered by the `lint-sweep` skill, never by
guessing what's wrong or editing files freehand:**

    python3 loop-eng/daily-loop/.claude/skills/lint-sweep/scripts/lint_sweep.py

(Run from the repo root, inside a worktree — see the skill for the full worktree +
connector orchestration; the script alone only owns the maker-checker-spine part.)

This loop has a **memory** (`progress.md`) and a **harness log** (`loop.log`), both
under `loop-eng/daily-loop/`, both append-only, both written every beat — success or
failure. See `loop-eng/break-it-on-purpose/` for why both exist and what a beat that
fails *silently* looks like from the spine alone; this loop reuses that exact pattern
rather than reinventing it.

**Scope is an allowlist (`scope.txt`), not "everything under `loop-eng/`."** The
original course-provided starter kits are not ours to auto-reformat. Adding a
directory to `scope.txt` is a decision a human makes on purpose.
