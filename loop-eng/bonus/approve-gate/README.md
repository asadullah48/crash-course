# Approve Gate — a loop that stops and asks first

**Bonus project — human-in-the-loop (checkpoints before irreversible action).**

Every other project in this course only reads the world — a position, a paper list, a status code.
This one can **write**: it deletes files. And deleting is the one kind of action a loop must never
take unattended. So instead of just *telling* you that, this project makes the rule mechanical: the
script always shows its plan first, and the only way to make it delete anything is an explicit
`--approve` flag that nothing in the script itself will ever add on its own.

## Run it

```bash
git clone https://github.com/panaversity/agentfactory-labs.git
cd agentfactory-labs/crash-course/loop-eng/bonus/approve-gate
claude
```

Say **yes** when Claude asks whether you trust the folder. Then ask:

```
set up the approve-gate sandbox
```

That builds a small synthetic messy folder — some genuinely old junk files, some fresh ones, and
one plain `notes.md` that is never a candidate no matter how old it gets. Now ask for the plan:

```
what would approve-gate clean up?
```

```
  🚪  APPROVE GATE  ·  .../sandbox
  ------------------------------------------------------------
     - build.log              40.0d old      1,200B
     - session.tmp            25.0d old        300B
     - crash-2026-01.log      33.0d old        900B
     - old-render.bak         60.0d old      4,096B
     4 file(s), 6,496 bytes would be deleted.
     (3 file(s) kept: wrong extension, or under 14d old)
  ------------------------------------------------------------
   DRY RUN -- nothing was deleted. Re-run with --approve to actually delete these.
```

Nothing happened. That printout is a *proposal*, not an action.

## Now say yes — and only then

```
yes, delete them
```

Only after you say something like that, in your own words, does Claude re-run the script with
`--approve` and the files actually go. Try the other direction too: ask for the plan again, then
change your mind and say nothing, or say "not yet" — and confirm nothing was deleted. The gate
holds either way.

## Why the flag lives in the script, not just in an instruction

A `SKILL.md` could simply *say* "ask before deleting," and most of the time an agent would honor
it. This project does not trust "most of the time" for an irreversible action. The dry run is the
script's *default behaviour* — no prompt has to remember to ask for it — and the only path to an
actual deletion is a flag that only a human's explicit words are supposed to trigger. The rule is
enforced by what the code does, not only by what the instructions say.

## How this differs from every other loop here

Sky Watch and Paper Watch run **unattended**, on purpose — the whole point is that nobody has to be
there. This project is the deliberate exception: some actions must never run unattended, no matter
how good the loop's judgment has been so far. A loop that has been right 50 times in a row is not
thereby trusted to be right the 51st time it deletes something. That is why every run starts over
at "show me the plan," never "you approved something like this before."

## What it ships

| File                                            | Job                                                                    |
| ------------------------------------------------ | ------------------------------------------------------------------------ |
| `.claude/skills/approve-gate/`                    | Owns the plan/approve rule — dry run by default, always                  |
| `.claude/skills/approve-gate/scripts/gate.py`     | Builds the sandbox, scans it, and is the *only* thing allowed to delete  |
| `.claude/settings.json`                           | Two narrow pre-granted rules: the skill, the script — no network needed  |
| `AGENTS.md`                                       | Points any agent at the skill/script — read by every agent               |
| `CLAUDE.md`                                       | One line — imports `AGENTS.md` so Claude Code reads it too               |

## Safety note

`gate.py` never looks outside its own `sandbox/` folder — that path is hard-coded next to the
script, not passed in. It is safe to actually run `--approve` for real, because there is nothing
real within its reach.
