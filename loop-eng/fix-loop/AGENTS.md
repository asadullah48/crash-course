# A Fix Loop with a Real Checker

This project has one job: fix one real bug through a maker-checker loop, where the
implementer and the reviewer are genuinely separate roles, and a PR only happens on a
real PASS.

**Fixing a bug through this loop means following the `fix-loop` skill's steps, in
order — worktree, fix, reproduce, then hand off to the `fix-reviewer` agent:**

    (implementer) work in an isolated worktree/branch, fix the bug, verify it, commit
    (reviewer)    run/read the diff independently, end with VERDICT: PASS or FAIL

(In Claude Code the implementer steps run automatically through the `fix-loop` skill,
and the grading runs through the `fix-reviewer` agent; any other agent should follow
`.claude/skills/fix-loop/SKILL.md` and `.claude/agents/fix-reviewer.md` directly.)

The one thing worth stating up front: **the implementer never grades its own work.**
A PR is not "the fix looks right to me" — it is "an independent reviewer ran or read
the diff and said PASS, in its own words, with reasons." If the reviewer says FAIL,
there is no PR, and the reasons are the next thing to fix — not something to argue
past.
