# Approve Gate

This project has one job: show a cleanup plan for its own bundled sandbox, and never delete
anything without the user's explicit, this-turn approval.

**Any request to clean up the sandbox, see what would be deleted, or run the approve-gate demo is
answered by running this project's script — plan first, always, no flag:**

    python3 .claude/skills/approve-gate/scripts/gate.py

(In Claude Code this runs automatically through the `approve-gate` skill; any other agent should
run the script directly.) Only run it again with `--approve` after the user has explicitly said so
in their own words, this turn. Never infer approval from an earlier turn, from silence, or from the
plan simply looking reasonable.

The one thing to hold onto: this script only ever touches its own `sandbox/` folder. It is safe to
actually run for real, because there is nothing real for it to reach.
