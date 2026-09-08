# Make the Test Pass, Then Stop

This project seeds three failing tests in `sample/test_calc.py` against a buggy
`sample/calc.py`. The job: fix the code until the checker says pass, capped at 6 attempts.

**Never decide success yourself. Only the checker decides**, by running:

    python3 .claude/skills/test-loop/scripts/checker.py

(In Claude Code this runs automatically through the `test-loop` skill; any other agent
should run the script directly.) Read its exit code:

- `0` -> tests passed. Stop immediately. Report success.
- `1` -> tests still fail, attempts remain. Look at the pytest output above, fix one real
  thing, run the checker again.
- `2` -> capped at 6 attempts, tests still fail. Stop. This is **not** success -- report the
  cap was hit and that the fix approach needs rethinking, not another try.

Reset the attempt counter before a fresh run:

    python3 .claude/skills/test-loop/scripts/checker.py --reset

The loop is exactly this: run checker, branch on exit code, repeat. Nothing about whether
the code "looks right" matters -- only what the checker's exit code says.
