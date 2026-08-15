---
name: approve-gate
description: Show a cleanup plan for the bundled sandbox/ folder and never delete anything without the user's explicit, this-turn approval, by running this skill's bundled script. Use it whenever the user asks to clean up the sandbox, see what would be deleted, run the approve-gate demo, or wants to see a loop that requires human sign-off before an irreversible action. Always run without --approve first and show the plan; only ever add --approve after the user has explicitly said something like "yes, delete them" or "approved" in their own words this turn -- never infer approval from an earlier turn or from silence.
allowed-tools: Bash, Read
---

# Approve gate

This is the one project in the course where the loop can **write** -- it deletes files -- and
deleting is the one class of action a loop must never take unattended. The rule here is not just
written down, it is load-bearing: the script itself defaults to a dry run, and the only way to make
it delete anything is the `--approve` flag.

## The two-step shape, every time

1. **Show the plan** (no flag — this is always safe, always read-only):

   ```bash
   python3 .claude/skills/approve-gate/scripts/gate.py
   ```

   Report the plan exactly as printed: which files, how old, how much space. End by asking the
   user whether to proceed. Do not add `--approve` in this same call.

2. **Only after the user explicitly approves, in their own words, in this conversation** — words
   like "yes, delete them," "approved," "go ahead" — run it again with `--approve`:

   ```bash
   python3 .claude/skills/approve-gate/scripts/gate.py --approve
   ```

If there's no `sandbox/` yet, run `--setup` once to build the synthetic messy folder to practice on.

## The rule that must never bend

**Never pass `--approve` unless the human said so, this turn, in words.** Not because a check
earlier looked good. Not because "they'll probably want this." Not because the plan looks obviously
safe. An approval from three turns ago does not carry forward, and a plan looking safe is not the
same as being told to proceed. This skill exists specifically to make that boundary a script's
hard-coded behaviour, not just an instruction an agent could talk itself past.
