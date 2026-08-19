# Project 2: The Lint Hook

**Course:** [Harness Engineering](https://agentfactory.panaversity.org/docs/harness-engineering-crash-course)
**Concept:** 8 — Hooks (verification that runs itself)
**Difficulty:** Easy to Medium

Two hooks, one linter, and a genuine test of the difference between them. Every result
below actually happened in this exact repo, live, in the session that built this project
— nothing here is a simulated transcript.

## The setup

`app.py` — a two-line function, kept deliberately trivial so the linter's opinion is
the only thing that changes:

```python
def greet(name):
    return f"Hello, {name}!"
```

`.flake8` — a minimal config (just a line-length setting; flake8's default rule set,
including `F841` unused-variable, is on by default).

`.claude/settings.json` in this folder — the deliverable:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "py -m flake8 . >&2 || exit 2" }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "py -m flake8 . >&2 || exit 2" }
        ]
      }
    ]
  }
}
```

Two hooks, same linter, two different jobs:

- **`PostToolUse`** fires after every `Edit`/`Write` in this folder. If flake8 fails,
  its stderr is handed back to the agent as feedback for its *next* move. It cannot
  undo the edit that just happened — the edit is already on disk.
- **`Stop`** fires whenever the agent tries to end its turn, with no matcher (so it
  checks every time, not just after an edit). If flake8 fails, the turn does not end —
  the harness feeds the failure back and the agent is forced to keep going.

## Why the test ran against the repo's own settings, not this folder's

Same reason as [Project 1](../the-first-wall/README.md): a nested `.claude/settings.json`
two directories down only takes effect in a session opened *in* that subfolder. To fire
the drill for real, the two hooks above were mirrored (with an absolute `cd` so the
linter runs against the right folder) into this repo's own `.claude/settings.local.json`
for the length of the drill, then left in place pending cleanup — see the note at the
bottom.

## 1. The PostToolUse hook: feedback, not a gate

`app.py` was deliberately broken:

```diff
 def greet(name):
+    unused = 42  # deliberate break for the drill
     return f"Hello, {name}!"
```

The very next system message, unprompted, was:

```
PostToolUse:Edit hook blocking error from command: ...
.\app.py:2:5: F841 local variable 'unused' is assigned to but never used
```

**The critical thing to check, and it was checked:** at the moment that message arrived,
`app.py` on disk still had the unused variable in it. The hook did not, could not, undo
the `Edit` — the edit had already landed before the hook ever ran. All the hook could do
was report.

Acting on that feedback — with no instruction from the user, exactly like the curriculum
describes — the file was corrected:

```diff
 def greet(name):
-    unused = 42  # deliberate break for the drill
     return f"Hello, {name}!"
```

This time flake8 passed and the hook produced no output at all. That's the whole
mechanism: **a broken edit still happens; the agent finds out immediately afterward and
gets one turn to react.**

## 2. The Stop hook: an actual gate

`app.py` was broken again, on purpose, the same way. Then the turn was deliberately
ended — a plain text reply, no further tool calls — to see whether the Stop hook would
let it through while lint was still red.

It did not. The very next input back was:

```
Stop hook feedback:
[cd .../harness-eng/the-lint-hook && py -m flake8 . >&2 || exit 2]: ...
.\app.py:2:5: F841 local variable 'unused' is assigned to but never used
```

The turn had not actually ended. The harness intercepted the stop attempt itself and
handed the failure back as the next input — the agent could not "finish" while the
check was red, no matter what it said. The file was fixed, and the same ending was tried
again:

```diff
 def greet(name):
-    unused = 42  # deliberate break, testing the Stop gate this time
     return f"Hello, {name}!"
```

This time the turn ended cleanly — the next message that arrived was an ordinary
continuation, not an injected hook failure. **The gate held while the check failed, and
released the instant it passed.**

## The one-sentence difference

**Feedback informs; a gate enforces.**

`PostToolUse` cannot stop a bad edit from landing — it can only make sure the agent
hears about it one turn later. `Stop` cannot undo anything either, but it *can* refuse
to let the task count as finished, which is a different kind of power: it moves the
decision of "is this done" out of the agent's own judgment and into a command's exit
code. The pre-commit / CI layer the curriculum describes is the same idea moved one
level further out, to a place even a bypassed or confused agent can't talk its way past
(`git commit --no-verify` still exists locally, which is exactly why CI plus branch
protection, not a local hook, is the real last gate — see Project 1's honesty-principle
note for the same shape of caveat applied to deny rules).

## What actually happened, summarized

| Step | What was checked | Result |
|---|---|---|
| Break `app.py`, edit lands | `PostToolUse` runs `flake8` | Fails — feedback returned, **edit not undone** |
| Fix in response to feedback | `PostToolUse` runs `flake8` | Passes — silent |
| Break `app.py` again, try to end turn | `Stop` runs `flake8` | Fails — **turn blocked**, forced to continue |
| Fix, try to end turn again | `Stop` runs `flake8` | Passes — turn ends normally |

## A cleanup note, honestly logged

The two hooks above were mirrored temporarily into the repo's own
`.claude/settings.local.json` to make this drill possible at all (same reason as
Project 1). Unlike Project 1's deny-rule cleanup, removing these hooks afterward was
**not** blocked by Claude Code's permission classifier — it went through in the same
session that added them. Worth noting as a real, observed asymmetry: the classifier
that refused to let an agent quietly loosen a *permission* rule did not apply the same
caution to a *hook*, at least not here.

## Try it yourself

Open a fresh Claude Code session with **this folder** as your working directory, then:

1. Ask it to add an unused variable to `app.py` and watch what comes back immediately after.
2. Ask it to leave the file broken and end its turn. Watch whether it's allowed to.
3. Ask it to fix the file and try to stop again.
