# Codify the Body

**Dynamic-Workflows Interlude — Concept 8 (worktree) + Concept 11 (maker-checker),
reused rather than re-taught.**

[Project 4](../fix-loop/) fixed one bug by hand: implementer works in a worktree,
reviewer grades the diff, PR only on PASS. Every step was a separate turn in a
conversation. This project asks: what if that whole *body* — worktree, draft, review,
verdict — were one re-runnable unit instead of a sequence of things someone types?

There are two ways to get there, and this project shows both — one documented (it
needs your own hands on the keyboard), one actually built and run.

## Approach 1 — Claude Code's native dynamic workflows (documented, not run here)

Claude Code has a real, built-in feature for exactly this: **dynamic workflows.** You
describe the task, Claude writes a JavaScript orchestration script, a background
runtime executes it (`agent()` per candidate, run in parallel), and if a run does what
you wanted you save it from `/workflows` as a `/command` you can re-run later.

**This is a genuinely different mechanism from everything else in this course** — it
moves the plan out of a conversation and into a script, so intermediate results live
in script variables instead of Claude's context window. That's what makes "dozens to
hundreds of agents per run" tractable in a way turn-by-turn delegation isn't.

To try it yourself:

```text
use a workflow to draft fixes for these three issues in parallel worktrees, and have a reviewer grade each one
```

Claude Code will ask you to approve the plan (or run immediately, depending on your
permission mode), then run it in the background while your session stays free. Watch
it with:

```text
/workflows
```

Arrow keys select the run, Enter drills into a phase or agent, `p` pauses/resumes,
`x` stops it. **Once a run does what you want, select it and press `s`** to save its
script to `.claude/workflows/` (shared with the repo) or `~/.claude/workflows/`
(just you) — it then runs as its own `/name` command from then on, in any project.

**Why this project doesn't run that approach live:** dynamic workflows trigger only
from a prompt *you type yourself* at the interactive prompt — the docs are explicit
that it does not fire from `-p`, from an Agent SDK message not stamped as human input,
from a scheduled task, or from a webhook/PR comment relayed into a conversation. This
project is being built by an agent working through tool calls, not a human typing at
a keyboard, so there is no way for it to trigger `/workflows` itself. The instructions
above are exact and verified against the live docs (`code.claude.com/docs/en/workflows`,
fetched while building this project) — run them yourself to see the real thing.

*Dynamic workflows are a research preview. If anything here disagrees with what you
see in your own Claude Code, the docs win — check `/docs workflows` or the URL above.*

## Approach 2 — plain shell (built and run live, right here)

No JavaScript runtime, no `/workflows` view — just `for`, `&`, `wait`, and exit codes.
This is the version that runs anywhere a coding agent CLI does, Claude Code's own
`-p` flag included, or `opencode run`, or nothing at all if you just want to see the
engine work against pre-authored fixes:

```bash
bash .claude/skills/codify-body/scripts/run_fix_loop.sh
```

What it does, all from that one command:

1. **`for name in candidates/*`** — one iteration per candidate.
2. **Isolate**: `git worktree add` gives each candidate its own checkout, so three
   fixes can be drafted at once without touching each other's files (Concept 8).
3. **Draft**: applies that candidate's `fix.patch`. In a real deployment this one line
   is where a coding-agent call goes instead (`claude -p "fix candidates/$name/bug.py"`,
   `opencode run ...`) — everything else in the script is unchanged either way.
4. **Review**: runs `check.py`. Its exit code *is* the verdict — `0` = PASS, anything
   else = FAIL. No LLM judgment call in this version, on purpose: a script-based
   checker is exactly what "use the reviewer's exit code as the checker" means.
5. **`&` on every iteration, then one `wait`** — all three candidates run at once, and
   the script blocks until every one of them has finished before printing results.

### Run it twice — real output, both times

```
== fix loop: 3 candidate(s) ==
  issue-1-clamp        PASS
  issue-2-slugify      PASS
  issue-3-dedupe       FAIL
```

Both runs — the second from a brand-new subshell, `bash -c '...'`, with nothing
inherited from the first — produced this exact result. `issue-1-clamp` and
`issue-2-slugify` ship real, verified fixes. `issue-3-dedupe` ships a **deliberately
bad** one: it changes `list(set(items))` to `sorted(set(items))`, which looks like a
sensible dedup fix and does remove duplicates — but sorts instead of preserving
first-seen order, so it's still wrong. The checker's exit code caught it both times,
exactly like the reviewer did by hand in Project 4 — just without anyone watching.

### Prove the interlude's warning: this engine has no memory

Both runs above used a fresh `mktemp -d` for worktrees, a fresh timestamp for branch
names, and read the same static `candidates/` directory from scratch. Nothing was
written anywhere between them. That's not an oversight — open a **new terminal**, or
just call the script again, and you'll get the identical three verdicts every time,
because there is nothing for it to remember. Compare that to
[`morning-brief`](../morning-brief/)'s `progress.md`: that project reads a bookmark
before it starts and writes one when it's done, specifically so a second run knows
what a first run already found. This script does neither. Every run starts over.

## What this would need to become a loop

Naming these two things is the point of the exercise — if you can name them, you
understand the difference between an engine and a loop:

1. **A heartbeat to fire it.** Right now a human runs the command. To make it fire on
   its own it would need one of the four kinds from this course: a schedule
   (`/schedule` — check for new candidates every morning), an event (something like
   [the doorbell](../doorbell/) — fire when a new issue is filed), or a bounded
   `/goal`/`/loop` if the trigger is "keep trying until every candidate passes."
2. **A progress file its agents write.** Right now every candidate is re-drafted and
   re-reviewed from scratch, every single run — there's no record of "issue-1-clamp
   already passed, skip it next time" or "issue-3-dedupe failed twice, stop retrying
   it." A spine like `morning-brief`'s `progress.md` — read first, written last — is
   what would let a second run build on the first instead of redoing everything.

An engine runs the body once, completely, every time you call it. A loop is that same
body plus a reason to run again on its own, and a memory of what it already did. This
project deliberately ships only the first half.

## What it ships

| File | Job |
| --- | --- |
| `.claude/skills/codify-body/scripts/run_fix_loop.sh` | The whole engine: for-loop, worktree isolation, patch-as-draft, checker-exit-code-as-review, fan-out, `wait`. |
| `candidates/issue-1-clamp/`, `issue-2-slugify/`, `issue-3-dedupe/` | Three independent small bugs, each with `bug.py`, `check.py` (the checker), and `fix.patch` (the pre-authored draft — two correct, one deliberately wrong). |
| `.claude/settings.json` | Pre-granted rules for the script and `git worktree` so it doesn't stop to ask each candidate. |
| `AGENTS.md` / `CLAUDE.md` | Point any agent at the script. |
