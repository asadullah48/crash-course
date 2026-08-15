# Budget Watch

This project has one job: report the real, live GitHub API rate-limit budget, and warn before it
runs out.

**Any question about API budget, rate limits, or whether a loop is about to run out of quota is
answered by running this project's script, never from memory or a guess:**

    python3 .claude/skills/budget-watch/scripts/budgetwatch.py

(In Claude Code this runs automatically through the `budget-watch` skill; any other agent should
run the script directly.) The script owns the fetch and the warn-threshold decision.

The one thing to hold onto: checking the budget spends part of the budget. Report that honestly --
it is not a footnote, it is the reason this project exists.
