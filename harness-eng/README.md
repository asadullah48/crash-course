# Harness Engineering — Projects

Projects for [Harness Engineering: A Crash Course](https://agentfactory.panaversity.org/docs/harness-engineering-crash-course).

A harness is everything around the model that decides what it's allowed to do —
permission rules, sandboxes, hooks, and the error text a connector hands back —
enforced by the tool layer, not by asking nicely in a prompt. These projects each take
one guardrail and make you actually try to break it.

## Concepts and Projects

| # | Concept | Project |
| --- | --- | --- |
| 7 | AX (design the harness for the agent that uses it) | [The Error Audit](the-error-audit/) |

## Prerequisites

[Claude Code](https://code.claude.com). Project 3 also needs Python 3.10+ (stdlib only,
no extra packages) and a network connection for its two live GitHub API calls.

## A note on branch order

Project 1 ("The First Wall," Concept 4) and Project 2 ("The Lint Hook," Concept 8) were
each built and opened as their own PR before this one, all off the same `main`. Whichever
merges first, this file's table gains that project's row on merge; add the others back by
hand if this one lands first. None of the three projects' files depend on each other.
