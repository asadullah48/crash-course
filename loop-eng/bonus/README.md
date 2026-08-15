# Loop Engineering — Bonus Projects

**Not part of the official crash course.** The 5 projects one level up map to specific numbered
concepts from [Loop Engineering: A Crash Course](https://agentfactory.panaversity.org/docs/loop-engineering-crash-course)
(4, 5, 6, 7, 12). These four fill gaps in *this fork* — loop-engineering patterns the official
numbering doesn't cover here — built in the same spirit: small, real, no API key, run it and feel
the idea rather than read about it.

## Projects

| Pattern | Project |
| --- | --- |
| Retry loops (error recovery) | [The Flaky Line](flaky-line/) |
| Bounded loops (self-limiting, not just self-scheduling) | [Budget Watch](budget-watch/) |
| Human-in-the-loop (checkpoints before irreversible action) | [Approve Gate](approve-gate/) |
| Self-review loops (generator + critic) | [Polish Loop](polish-loop/) |

## How these fit the 5 official projects

Each core loop-eng project teaches one **heartbeat** (what starts a run) or the **spine** (what a
run remembers). These four teach the other half of building a real loop: what happens when the
call it makes **fails** (Flaky Line), when the resource it depends on is **finite** (Budget Watch),
when the action it wants to take is **irreversible** (Approve Gate), and when "done" has to be
**proven**, not assumed (Polish Loop). None of the five official projects need any of these —
which is exactly why they're worth a project of their own.

## Prerequisites

Same as the rest of loop-eng: [Claude Code](https://code.claude.com) and an internet connection.
Three of the four use live public APIs that need no key and no sign-up; Approve Gate and Polish
Loop need no network at all.
