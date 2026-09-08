# Project 12 — Build a Dreaming Loop

*Difficulty: Capstone · Uses: Concept 12 (spine and improvement loop), Concept 11
(maker-checker), Concept 6 (schedule), Part 5 (human gate)*

The official brief (Loop Engineering appendix, "Practice: three routine drills" —
Project 12 is not a drill, it's the second capstone that closes the section):

> You need a loop that has already run for a week and left dated entries in
> `progress.md` (Project 3 or Project 8 gives you one). Now build a second loop
> over it. On a weekly schedule, it reads all log entries since the date in its
> own `dreaming-state.md`, looks for any failure or correction that appears more
> than once, and drafts the smallest rules-file or skill change that would
> prevent it, as a PR on a `claude/` branch, never a direct commit. The PR
> description must cite its evidence: which runs, how often, and why this line
> stops it. Have it also propose one deletion: a rule no recent run needed.
> Finish by updating `dreaming-state.md`.
>
> **Done when** three things are true. The PR's proposed change traces to real,
> cited log entries, not a plausible-sounding guess. A deliberately planted
> repeated failure in the logs (add one by hand) gets caught and turned into a
> proposal. And nothing changed in your rules file without you merging it.

## Part 0 — a real bug had to be fixed before this project could even start

`loop-eng/daily-loop/progress.md` was supposed to be Project 8's week of history.
It wasn't. `progress.md` and `loop.log` were gitignored repo-wide (fine for a
project run locally by a human — the file just sits on disk between
invocations) but Project 8 runs as an **unattended cloud routine**, which
clones fresh every single beat. A gitignored file never reaches a fresh clone
(the exact A4 lesson from Project 10, just applied to a spine file instead of a
secret). Three real beats had already run before this was caught, and each one
only ever saw its own single entry — the previous beat's write was thrown away
the moment its session ended. `progress.md` had never even been committed to
git.

**The fix**, on this PR: `loop-eng/daily-loop/.gitignore` un-ignores both files
for this project specifically, and `SKILL.md` gained two new steps — restore
the spine from a dedicated, force-pushed, never-merged branch
(`claude/daily-loop-spine`) before each beat runs, and persist it back to that
same branch after, every beat, every exit code. See that PR's commit for the
full story; see `claude/daily-loop-spine` for where the spine actually lives
now.

## Part 1 — a real week, honestly labeled

`claude/daily-loop-spine` holds nine dated entries, 2026-08-11 through
2026-08-17. **Six are backdated/seeded by hand** (08-11 through 08-16),
exactly as the project's own instructions require ("plant a repeated failure
manually in the logs to test detection"). **Three are real**, copied verbatim
from actual `daily-lint-sweep` routine run transcripts this session (all
2026-08-17, all clean).

The planted repeated failure: the same `F841` (ruff-unfixable) issue in
`loop-eng/break-it-on-purpose/.claude/skills/morning-brief/scripts/brief.py`,
logged on **2026-08-13** and again on **2026-08-16**.

## Part 2 — the dreaming loop itself

One routine, `dreaming-loop` (`trig_01WPUuvbweMxndiNCaDYjff5`), designed to
fire weekly. Its prompt:

1. Reads `progress.md`/`loop.log` from `claude/daily-loop-spine` (not the
   default branch — that's where the real history lives).
2. Reads `loop-eng/dreaming-loop/dreaming-state.md` on the default branch to
   know where the last run left off (first run: no state file, consider
   everything).
3. Looks for any failure/correction appearing more than once in that window.
4. Drafts the smallest real rules/skill-file change, reading the actual
   relevant files first — never a generic guess.
5. Separately proposes exactly one settings.json permission for deletion, with
   evidence, but does **not** edit the file itself (see Attempt 1 below for
   why).
6. Opens a PR on a `claude/dreaming-loop-<date>` branch citing all evidence,
   including the deletion suggestion as text for a human to apply by hand.
7. Never merges anything itself.

### Attempt 1 — a real platform guardrail, not a bug in the prompt

The first test run (session `cse_01TcHBS9fRcBLokqUWKj9MYK`) investigated
thoroughly — it even ran `ruff check` on the *current* `brief.py` and correctly
noticed the file passes clean today, and started digging through git history
to reconcile that against the log's claim before proposing anything. It never
got to finish: when it tried to literally edit
`loop-eng/daily-loop/.claude/settings.json` for the deletion proposal, it hung
on `worker_status: "requires_action"` — **Claude Code's own harness blocks
unattended writes to any `.claude/settings.json` file**, as a guardrail
against a session silently widening its own permissions, regardless of the
routine's general `Edit` access. An unattended routine has nobody to approve
that prompt, so the run just sat there. The prompt was rewritten to describe
the deletion as text in the PR body instead of a file edit, and the routine
was re-fired.

### Attempt 2 — the real, evidence-cited result

Session `cse_01Gd9rQiNGvF45t9kfyUFgiX`, 47 turns, ~7.5 minutes, opened
**[PR #14](https://github.com/asadullah48/crash-course/pull/14)**. What it
actually did, verified independently of its own summary:

- **Found** the repeated `F841` failure, cited both exact timestamps.
- **Did not trust the log text at face value.** It ran `ruff check` against
  the real current file, got a clean result, and rather than either blindly
  proposing a fix or giving up, it went and tested ruff's real behavior
  directly: wrote synthetic test files, confirmed `F841`'s fix is classified
  `"applicability": "unsafe"` even in the simplest possible case, and
  confirmed `ruff check --fix` (what `lint_sweep.py`'s maker calls) never
  applies unsafe fixes by default. That's the actual mechanical reason the
  logged beats failed — verified, not assumed.
- **Proposed the smallest real fix**: a new `ruff.toml` scoped to just the
  lint-sweep skill's own ruff calls, promoting only `F841` to a safe fix
  (`extend-safe-fixes`) — not the blanket `--unsafe-fixes` flag, which would
  have hedged every unsafe fix in ruff's whole rule set to an unattended
  maker. It wired this into `lint_sweep.py` and verified the script still ran
  clean against the real repo.
- **Proposed the deletion** (`"Skill(lint-sweep)"` from `settings.json`) as PR
  text, with evidence: `SKILL.md`'s workflow is documented as plain `Bash`
  commands the routine follows directly, never a formal `Skill` tool call, and
  nothing in the logged window shows evidence of one being needed.
- **Updated `dreaming-state.md`**, recording `2026-08-17 19:41 UTC` as the
  latest processed entry.
- **Responded to real automated code review.** The repo's own installed bots
  (Sourcery, and the `claude-review` GitHub Action from Project 6) reviewed
  the PR automatically. Sourcery flagged a genuine subtlety: passing
  `--config` on *every* ruff call meant the checker also picked up the custom
  config, not just the maker — a real risk to the maker-checker separation
  (Concept 11) if it meant the checker started trusting F841 findings as
  already-safe. The loop verified this was actually a behavioral no-op
  (`extend-safe-fixes` only changes reported fix-*applicability* metadata,
  never which issues are found), fixed the scoping anyway so the intent reads
  clearly in the code, ran a full end-to-end test with a real `F841` case
  (maker fixes it, exits 2, checker independently confirms clean), pushed a
  second commit, and replied to the review explaining exactly what changed and
  why.

## Done-when, checked

- ✅ **The PR's proposed change traces to real, cited log entries.** Exact
  timestamps, exact file/line/rule, and the root cause independently verified
  against live `ruff` behavior rather than trusted from the log text.
- ✅ **The planted repeated failure was caught and turned into a proposal.**
- ✅ **Nothing changed in the rules file without a human merging it.** PR #14
  is open, not merged. `settings.json` was never touched at all — the loop
  discovered and respected a real platform guardrail rather than working
  around it.

## One sentence

An improvement loop is only as trustworthy as its evidence discipline —
watching this one refuse to propose a fix for a failure it couldn't verify
against the live tool, and separately refuse to route around a permissions
guardrail it wasn't supposed to have, is a better demonstration of "don't
guess" than anything in the prompt could have stated on its own.
