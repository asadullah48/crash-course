# Make the Test Pass, Then Stop

**Loop Engineering — conditional loops (run until done) + maker-checker (an independent
checker decides, not the one doing the work).**

Three tests fail on purpose against a buggy `sample/calc.py`. A loop tries to fix it,
capped at 6 attempts, and stops the instant an independent test run says pass — never
because the code *looks* fixed, never because attempts ran out.

## Run it

```bash
cd loop-eng/test-loop
claude
```

Say **yes** when Claude asks whether you trust this folder. Then type:

```
make the tests pass, capped at 6 attempts
```

What happens each round:

1. Claude runs the checker: `python3 .claude/skills/test-loop/scripts/checker.py`
2. The checker runs `pytest` against `sample/`, tracks the attempt count, and returns:
   - **exit 0** → pytest passed. Loop stops. Success.
   - **exit 1** → pytest failed, attempts remain. Claude reads the failure, fixes one thing
     in `sample/calc.py`, and runs the checker again.
   - **exit 2** → 6 attempts used, still failing. Loop stops. **Not** success — Claude says
     so plainly instead of pretending it worked.

Reset between runs with `python3 .claude/skills/test-loop/scripts/checker.py --reset`.

## Why "maker-checker" and not just "try until it works"

The tempting shortcut is to let the same agent that wrote the fix also decide whether the
fix worked — "I changed the divisor, that should do it." That is not verification, it is
optimism with extra steps.

Here the checker is a separate, dumb, opinion-free step: it shells out to `pytest`, reads
*pytest's* exit code, and reports one of three outcomes. The agent making the fix (the
**maker**) never gets to grade its own work — the test runner (the **checker**) does, every
single time, including the 6th.

## The one thing to notice

Exit code `2` exists specifically so "ran out of attempts" can never be confused with
"passed." A loop that treats hitting the cap as good enough isn't a conditional loop
anymore — it is a fixed number of tries dressed up as a stopping condition. If a real run
of this project keeps landing on exit `2`, that is the loop telling you the fix strategy
needs to change, not a sign to raise the cap to 7.

## What it ships

| File | Job |
| --- | --- |
| `sample/calc.py` | Buggy module — three seeded bugs, fixed live during the loop. |
| `sample/test_calc.py` | Three tests, one per bug, failing until each is fixed. |
| `.claude/skills/test-loop/scripts/checker.py` | Owns the pytest call, the attempt count, and the three-way exit code. |
| `.claude/settings.json` | Pre-granted rule so the loop never stops to ask permission each attempt. |
| `AGENTS.md` / `CLAUDE.md` | Point any agent at the skill/script. |
