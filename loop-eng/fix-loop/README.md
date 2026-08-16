# A Fix Loop with a Real Checker

**Loop Engineering — worktrees (isolated checkouts) + skills (the implementer's steps)
+ maker-checker (an independent reviewer decides, not the implementer).**

Every other project in this course has one loop. This one has two roles that are not
allowed to be the same voice: an **implementer** who fixes a bug in its own worktree,
and a **reviewer** — a separate agent — who independently re-verifies the fix and
replies `VERDICT: PASS` or `VERDICT: FAIL`, with reasons. A PR only happens on PASS.

## The bug this project fixes, for real

[`morning-brief`](../morning-brief/)'s `count_todos()` counts occurrences of the
literal words "TODO" and "FIXME" anywhere in the repo — including inside prose that
*talks about* TODO/FIXME counting, like its own docstrings and README. Reproduced:
`git grep -nIE "TODO|FIXME"` returns 14 matches, and every single one is prose — zero
are real comment-style TODOs.

## Run it

```bash
cd loop-eng/fix-loop
claude
```

Say **yes** when Claude asks whether you trust this folder. Then ask:

```
fix the TODO/FIXME over-counting bug through the fix loop
```

What happens:

1. **Implementer** (`fix-loop` skill): creates a worktree, reproduces the over-count,
   writes the smallest fix — only match TODO/FIXME when it follows a real comment
   marker (`#`, `//`, `<!--`), not anywhere in a sentence — re-runs the reproduction to
   confirm it now reports the correct count, commits.
2. **Reviewer** (`fix-reviewer` agent): independently re-runs the reproduction against
   the fixed code rather than trusting the implementer's account, reads the diff, and
   ends with `VERDICT: PASS` or `VERDICT: FAIL` plus concrete, checkable reasons.
3. **PASS** → the implementer pushes the branch and opens a PR, with the reviewer's
   reasoning included. **FAIL** → no PR. The reasons go back to the implementer.

## Prove the checker isn't a rubber stamp

The lesson isn't complete until the reviewer has actually rejected something. This
project's own build included a second, deliberately bad "fix": instead of correcting
the matching logic, it added a pathspec excluding morning-brief's own files from the
search — a plausible-looking patch that reduces the symptom without touching the root
cause. Two independent flaws made it a genuinely bad fix, not an obviously silly one:

- It still leaves at least one unrelated prose match elsewhere in the repo untouched
  (the underlying "match TODO anywhere" logic is still there, just narrowed).
- The exclude path is relative to the working directory, and the script is meant to be
  run from *inside* `loop-eng/morning-brief/` (per its own README) — so the exclusion
  doesn't even line up with how the tool is actually invoked. Testing it from the repo
  root (a natural first check) looks like it worked; testing it the way a real user
  runs it does not.

A reviewer that only skims a diff — or only reruns things the same casual way the
implementer did — can miss exactly this kind of gap. **A checker that approves
everything is no checker;** the fix only counts once something has actually been
caught and failed for a real, checkable reason.

## What it ships

| File | Job |
| --- | --- |
| `.claude/skills/fix-loop/SKILL.md` | The implementer's steps: reproduce, isolate, fix, re-verify, commit, hand off. |
| `.claude/agents/fix-reviewer.md` | The reviewer: independently verifies and grades, ends with `VERDICT: PASS/FAIL`. |
| `.claude/settings.json` | Pre-granted rules for `git worktree` and `gh pr` so the loop doesn't stop to ask each step. |
| `AGENTS.md` / `CLAUDE.md` | Point any agent at the skill/agent. |

## The one thing to notice

The implementer and the reviewer look at the *same* diff and the *same* kind of
reproduction — and still reach independent judgments, because the reviewer re-runs
things itself instead of trusting the account it was handed. Collapse them back into
one voice grading its own work, and "PASS" stops meaning anything.
