# Harness Engineering — Projects

Projects for [Harness Engineering: A Crash Course](https://agentfactory.panaversity.org/docs/harness-engineering-crash-course).

A harness is everything around the model that decides what it's allowed to do —
permission rules, sandboxes, hooks — enforced by the tool layer, not by asking nicely in
a prompt. These projects each take one guardrail and make you actually try to break it.

## Concepts and Projects

| # | Concept | Project |
| --- | --- | --- |
| 8 | Hooks (verification that runs itself) | [The Lint Hook](the-lint-hook/) |

## Prerequisites

[Claude Code](https://code.claude.com) (the `hooks` block in `settings.json` is a Claude
Code feature; OpenCode's equivalent is a `.opencode/plugins/*.ts` plugin, mentioned in
each project's README where relevant).

## A note on branch order

Project 1 ("The First Wall," Concept 4) was built and opened as its own PR before this
one, off the same `main`. If that PR merges first, this file's table gains a row above
this one on merge; if this one merges first, add Project 1's row back by hand. Either
way, nothing here depends on the other project's files.
