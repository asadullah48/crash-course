# Codify the Body

This project has one job: take the fix loop's BODY -- worktree, draft, review, verdict
-- and turn it from a sequence of steps someone runs by hand (Project 4) into one
re-runnable unit that does all three candidates at once.

**Running the whole thing is one command, never a step-by-step walkthrough:**

    bash .claude/skills/codify-body/scripts/run_fix_loop.sh

It fans out one isolated `git worktree` per candidate under `candidates/`, applies that
candidate's `fix.patch`, runs its `check.py`, and prints PASS/FAIL for each -- all in
parallel, all from one invocation.

The one thing worth stating up front: **this script has no memory.** It does not read
a file from its last run and it does not skip a candidate because it passed before.
Every run is the same static `candidates/` directory processed from scratch. That is
deliberate -- this is an engine, not a loop, and the difference is exactly what's
missing: no heartbeat firing it on its own, no progress file it writes to remember
what happened last time.
