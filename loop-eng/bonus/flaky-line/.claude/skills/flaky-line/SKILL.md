---
name: flaky-line
description: Call a public endpoint that fails on purpose some of the time, retrying with exponential backoff, by running this skill's bundled script -- never by simulating the retries yourself. Use it whenever the user asks to test retry logic, see a retry loop in action, watch exponential backoff, simulate a flaky or unreliable API, or ask what happens when every retry fails. The script owns the calling, the backoff timing, and the honest give-up -- report exactly what it printed.
allowed-tools: Bash, Read
---

# Flaky line

A retry loop is not "try again until it works" -- that is a loop that never learns to give up.
A real retry loop backs off between attempts (so it does not hammer a struggling server), and it
has a limit (so it does not run forever). This skill's script is that loop, made visible: every
attempt, every wait, and the two honest endings -- it worked, or it truly did not.

## Running it

```bash
python3 .claude/skills/flaky-line/scripts/flakyline.py
```

To see it fail on purpose and watch the honest give-up:

```bash
python3 .claude/skills/flaky-line/scripts/flakyline.py --codes 500,503
```

To see it succeed on the first try, no retries needed:

```bash
python3 .claude/skills/flaky-line/scripts/flakyline.py --codes 200
```

## The one rule

Report the script's own output. Do not paraphrase "it took a few tries" -- show the attempt log,
because the number of attempts and the backoff delays are the entire point of running this.

If every attempt fails, say plainly that it failed after N attempts. Do not imply it "basically
worked" or soften a real failure -- a retry loop that cannot be honest about failing is worse than
one with no retries at all.
