# Polish Loop

This project has one job: write an elevator pitch and revise it until an independent, mechanical
critic — not your own judgment — agrees it is done.

**Any request to write or polish a pitch is answered by the write/grade/revise loop, never by
declaring it finished yourself:**

1. Write or rewrite `pitch.md`.
2. Grade it: `python3 .claude/skills/polish-loop/scripts/critic.py`
3. Fix what failed. Repeat until it prints `5/5 passing`.

(In Claude Code this runs through the `polish-loop` skill; any other agent should run the script
directly.) The script owns the rubric. It is not yours to edit to make a check pass.

The one thing to hold onto: you are the generator, the script is the critic, and only the critic
says PASS. A generator that grades its own work is not a self-review loop.
