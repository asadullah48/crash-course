# Harness Engineering — Projects

Projects for [Harness Engineering: A Crash Course](https://agentfactory.panaversity.org/docs/harness-engineering-crash-course).

A harness is everything around the model that decides what it's allowed to do —
permission rules, sandboxes, hooks, and the error text a connector hands back —
enforced by the tool layer, not by asking nicely in a prompt. These projects each take
one guardrail and make you actually try to break it.

## Concepts and Projects

| # | Concept | Project |
| --- | --- | --- |
| 9 | Typed Output | [The Typed Reviewer](the-typed-reviewer/) |

## Prerequisites

[Claude Code](https://code.claude.com), and `jq` on `PATH` (a small command-line JSON
tool — `winget install jqlang.jq`, `brew install jq`, or your platform's package
manager) to run this project's validator.

## A note on branch order

Project 1 ("The First Wall," Concept 4), Project 2 ("The Lint Hook," Concept 8),
Project 3 ("The Error Audit," Concept 7), and Project 4 ("The Tool Diet," Concepts 6+7)
were each built and opened as their own PR before this one, all off the same `main`.
Whichever merges first, this file's table gains that project's row on merge; add the
others back by hand if this one lands first. Project 5 depends on none of them
directly -- it reads (never modifies) `harness-eng/the-lint-hook/app.py` (Project 2's
fixture) and quotes, without editing, `loop-eng/portfolio-starter/.claude/agents/reviewer.md`
from the prior Loop Engineering course.
