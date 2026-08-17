# Loop Engineering — Projects

Projects for [*Loop Engineering: A Crash Course*](https://agentfactory.panaversity.org/docs/loop-engineering-crash-course), part of [*The AI Agent Factory*](https://agentfactory.panaversity.org/docs/) curriculum. Facts about the curriculum itself in this README and in each project's own writeup were grounded against the book's live content via the **Agent Factory System of Record** MCP connector (the same source the **Zia Tutor AI** connector teaches from) — never assumed from memory, always checked against the current text.

## Overview

A loop runs on a **heartbeat** and remembers through a **spine**. This directory is not a read of that idea — it's twelve real loops built and actually run, in a real GitHub repo, most of them as genuine unattended cloud routines fired against a real repository, their transcripts read (not just their status), and their outcomes verified independently rather than trusted from their own summaries. Where a project claims something worked, that claim is backed by a session ID, a run log, or a diff you can open.

The five original course-provided starter kits (`iss-loop`, `portfolio-starter`, `sky-watch`, `doorbell`, `paper-watch`) live here unmodified, as downloaded — they're the spec-driven exercises the course hands you to build from scratch. Everything else in this directory is this fork's own build: the twelve numbered projects plus four bonus patterns, each in its own directory, each with its own branch and pull request, following one consistent discipline throughout — **branch → build → test for real → commit with a detailed rationale → push → PR → merge only on request.**

## The 12 numbered projects, in order built

| # | Concept(s) | Project | What it actually proves |
| - | - | - | - |
| 1 | 4 — In-session loops | [`watch-loop`](watch-loop/) | A loop that repeats while you watch, stopping only when a real command says done. |
| 2 | 5 + 11 — Conditional loop, maker-checker | [`test-loop`](test-loop/) | Run-until-a-test-passes, with the checker never grading its own work. |
| 3 | 6 + 12 — Schedule, the spine | [`morning-brief`](morning-brief/) | A scheduled loop with real memory: reads `progress.md` first, writes it last. |
| — | fix | [`fix/todo-overcount`](https://github.com/asadullah48/crash-course/tree/fix/todo-overcount-good) | A real bug found in Project 3's counting logic, fixed and verified. |
| 6 | 7 — Event-driven loops | [`doorbell-loop`](doorbell-loop/) | Reacts to a GitHub PR event via the Claude GitHub Action — no schedule, no polling. |
| 7 | 13 + 14 — Cost, observability | [`break-it-on-purpose`](break-it-on-purpose/) | Project 3's loop deliberately sabotaged, then diagnosed from the spine + harness log alone. |
| 8 | Capstone — all six parts | [`daily-loop`](daily-loop/) | Heartbeat, worktree, skill, maker-checker, connector, spine — a real unattended cloud routine (`daily-lint-sweep`), fired for real, more than once. |
| 9 | A1, A3, A5 | [`prove-a-prompt`](prove-a-prompt/)¹ | One routine fired twice proves the platform's own lesson: green only means the session exited cleanly, never that the task succeeded. |
| 10 | A4, A2 | [`secrets-drill`](secrets-drill/)¹ | The same drill, for credentials: a `.env` file physically cannot reach a fresh cloud clone; the environment-variables panel can. |
| 11 | A3, A4, A6 | [`two-routine-gate`](two-routine-gate/)¹ | The Part 5 human gate built from two real routines — one that can *only* run because a human fired it by hand. |
| 12 | Capstone — 12, 11, 6, Part 5 | [`dreaming-loop`](dreaming-loop/)² | A second loop that reads the first loop's real history and opens an evidence-cited PR proposing its own improvement — never guessing, never merging itself. |

¹ Built on branches not yet merged to `main` at the time this README was written — open the linked PR to see the code before it merges: [`prove-a-prompt` → PR #9](https://github.com/asadullah48/crash-course/pull/9), [`secrets-drill` → PR #10](https://github.com/asadullah48/crash-course/pull/10), [`two-routine-gate` → PR #11](https://github.com/asadullah48/crash-course/pull/11).
² Two PRs: [#15](https://github.com/asadullah48/crash-course/pull/15) (the project + a real bug fix it depended on) and [#14](https://github.com/asadullah48/crash-course/pull/14) (opened by the dreaming loop itself, proposing a real fix to Project 8).

## Explanation, one line per topic

- **In-session loops** repeat inside a chat you're watching; they die the moment you close the terminal, because they never left your machine.
- **Conditional loops** run until a *command* says done — never the model's own opinion of its work, which is the whole reason a checker exists.
- **Scheduled loops** fire on a clock, on someone else's servers, whether or not your laptop is open.
- **The spine** is the one file a fresh, memory-less clone reads first and writes last — the only thing that makes "no memory between runs" survivable.
- **Event-driven loops** wait for nothing to happen, then react the instant something does — the opposite failure mode of a schedule.
- **Cost & observability** mean a loop's own log has to answer "what did this cost, and what actually happened" without you re-reading every transcript.
- **The capstone (six parts)** is every prior concept wired together on purpose: heartbeat, isolation, instructions, a real checker, a way to ship, and memory.
- **One-off schedules (A1/A3)** are the free way to rehearse a routine's prompt before trusting it to a recurring clock — and the one place the platform's status column is proven to lie about task success.
- **Secrets (A4)** only ever belong in the environment-variables panel; a `.env` file is a promise a fresh cloud clone cannot keep.
- **The human gate (A3/A4/A6)** is two routines, not one — a drafter that can only draft, and an executor that can only run because a person decided to fire it.
- **The dreaming loop (capstone of capstones)** closes the loop on the loops themselves: it reads real history, cites real evidence, and proposes — never applies — its own improvement.

## Bonus projects (this fork, not part of the official numbering)

Four more loop-engineering patterns the numbered concepts don't cover: retry loops, bounded loops, human-in-the-loop checkpoints, and self-review loops. See [`bonus/`](bonus/) for all four.

## A related, real example: portfolio-starter

[`portfolio-starter/`](portfolio-starter/) is the course's spec-driven exercise — no worked example is provided on purpose, you define "done" and build to it. For a real, finished instance of exactly that exercise, see **[asadullahshafique-devunity.vercel.app](https://asadullahshafique-devunity.vercel.app/)**.

## What's next

Loop Engineering is the 8th of 12 crash courses in the *General Agents* track. The next one in sequence is **[Harness Engineering: A Crash Course](https://agentfactory.panaversity.org/docs/harness-engineering-crash-course)** — constrain, inform, verify, correct, escalate: the five verbs that turn "a loop that works" into "a loop you'd trust unattended overnight." Several projects here already borrow from it directly (`daily-loop`'s `.claude/settings.json` permission allowlist, and the platform's own block on unattended `.claude/settings.json` writes that `dreaming-loop` ran into, are both harness-engineering territory).

After that comes **[Graph Engineering: A Crash Course](https://agentfactory.panaversity.org/docs/graph-engineering-crash-course)** — commit DAGs and knowledge graphs for when one loop's memory (a single `progress.md`) stops being enough, because a team of agents needs a shared brain, not twenty transcripts nobody re-reads. The course states its own prerequisite plainly: *"You need these first: Loop Engineering and Harness Engineering."* Worth knowing it exists, not worth starting yet.

## Prerequisites

[Claude Code](https://code.claude.com) and an internet connection. The starter-kit projects use live public APIs that need no key and no sign-up; the routine-based projects (9 through 12, and 8) need a claude.ai login with Routines access.
