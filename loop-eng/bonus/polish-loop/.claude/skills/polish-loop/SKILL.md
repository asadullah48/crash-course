---
name: polish-loop
description: Write and revise an elevator pitch (pitch.md) until it passes a fixed, mechanical rubric by running this skill's bundled critic script -- never by declaring it done from your own judgment. Use it whenever the user asks to write or polish an elevator pitch, wants a generator+critic feedback loop, wants to see self-review or self-correction in action, or asks what makes a pitch pass. You are the generator; the critic is the bundled script, and it is the only thing allowed to say PASS.
allowed-tools: Bash, Read, Write, Edit
---

# Polish loop

A self-review loop only works if the reviewer is not the same judgment as the writer. If the agent
that wrote the pitch also decides whether the pitch is good, it will always agree with itself.
This skill splits the two roles: **you** are the generator (you write and rewrite `pitch.md`), and
`critic.py` is the critic — a fixed rubric with no opinion, no mood, and no willingness to be
talked into a pass it did not earn.

## The loop

1. Write (or rewrite) the pitch into `pitch.md` in the project root — a 30-second elevator pitch,
   per `brief.md`.
2. Grade it:

   ```bash
   python3 .claude/skills/polish-loop/scripts/critic.py
   ```

3. Read exactly what failed — the script names each check and shows the offending detail.
4. Revise `pitch.md` to fix what failed. Do not touch `critic.py` to make a check pass — if a check
   feels wrong, say so and explain why, but the check itself is not yours to edit.
5. Run it again. Repeat until it prints `5/5 passing`.

## The one rule

**Only the critic script decides PASS.** Never tell the user the pitch is "done" or "good" based on
your own read of it — report the script's number, and if it isn't 5/5, say what's still failing and
keep revising. A generator that grades its own homework is not a self-review loop, it is a rubber
stamp.
