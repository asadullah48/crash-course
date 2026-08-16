---
name: fix-loop
description: Fix one real bug in an isolated worktree, then hand the diff to the fix-reviewer agent and only open a PR if it says PASS. Use whenever the user asks to fix a bug through the fix-loop, drive a maker-checker fix workflow, or wants a reviewer to grade a patch before it goes out as a PR.
---

# Fix Loop — the implementer's steps

You (the **maker**) do not decide whether your own fix is good enough. A separate
**checker** — the `fix-reviewer` agent — grades it. You only open a PR if it says PASS.

## The steps, in order

1. **Reproduce the bug first.** Run whatever shows the wrong behavior — a failing test,
   a script printing the wrong output, whatever proves the bug is real *before* you
   touch anything. If you can't reproduce it, you don't have a bug yet, you have a
   report.

2. **Isolate the work.** Create a worktree (`git worktree add <path> -b <branch>`) or at
   minimum a fresh branch. Never fix on `main` directly — the reviewer needs a clean
   diff to grade, and a rejected fix must be discardable without touching anything else.

3. **Write the smallest fix that addresses the actual cause**, not the symptom you
   noticed first. Resist the urge to also refactor nearby code — every extra line is
   one more thing the reviewer has to grade, and one more way to fail for reasons
   unrelated to the bug.

4. **Re-run the reproduction from step 1.** If it still shows the wrong behavior, you
   are not done — go back to step 3. Never hand off a fix you have not personally
   watched work.

5. **Commit** with a message that names the bug, not just "fix bug."

6. **Hand off to `fix-reviewer`.** Give it: the bug report, the diff, and how you
   reproduced the fix working. Do not summarize it favorably — give it everything it
   needs to disagree with you.

7. **Branch on the verdict:**
   - **PASS** → push the branch, open a PR. Include the reviewer's PASS reasoning in
     the PR description.
   - **FAIL** → do not open a PR. Read the reasons, fix them, go back to step 3 — or,
     if the reviewer is objecting to something that isn't actually wrong, that's a
     signal to look harder at step 3, not to argue with the checker.

## The one rule that makes this a maker-checker loop, not theater

**You never grade your own work.** If you catch yourself writing "this should be fine"
or "I'm confident this fixes it" as the reason a PR goes out, stop — that sentence is
supposed to come from the reviewer, in its own words, after looking at the diff.
