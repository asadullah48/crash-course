---
name: test-loop
description: Run the maker-checker loop for the test-loop project -- fix sample/calc.py until pytest passes, by running this skill's checker script and branching on its exit code, never by declaring success yourself. Use whenever the user asks to make the tests pass, run the test loop, or fix the code until it's green, capped at 6 attempts.
---

# Make the Test Pass, Then Stop

Run the checker. Branch on its exit code. Repeat. That is the whole loop:

    python3 .claude/skills/test-loop/scripts/checker.py

- **exit 0** -> tests passed. Stop immediately and report success. Nothing more to do.
- **exit 1** -> tests still fail, attempts remain. Read the pytest output the checker printed,
  fix one real thing in `sample/calc.py`, run the checker again.
- **exit 2** -> capped at 6 attempts, tests still fail. Stop. This is **not** success -- say so
  plainly, and note that the approach needs rethinking rather than a 7th try.

Reset the attempt counter before a fresh run:

    python3 .claude/skills/test-loop/scripts/checker.py --reset

**Never decide pass/fail yourself.** The checker's exit code is the only thing that ends the
loop -- not how the code looks, not confidence that "this should work now."
