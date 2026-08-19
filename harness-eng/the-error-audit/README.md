# Project 3: The Error Audit

**Course:** [Harness Engineering](https://agentfactory.panaversity.org/docs/harness-engineering-crash-course)
**Concept:** 7 — AX (design the harness for the agent that uses it)
**Difficulty:** Medium

One connector, three errors, rewritten so the agent that reads them can act
on them. Every result below is a real run captured in this session — the
two credential/file errors are live calls against the actual GitHub API;
the rate-limit leg is explained and disclosed below as the one exception.

## The connector

**GitHub's Contents API**, chosen because it's the connector this repo's
own loops already lean on hardest — every `loop-eng/` project in this
course uses `gh` under the hood, and this very session used `gh pr create`,
`gh auth token`, and `gh api` repeatedly to build the last two projects.

Two files, same shape as a before/after diff:

- `connector_before.py` — the naive version. Whatever the API says, the
  caller gets, verbatim.
- `connector.py` — the AX-rewritten version. Same call, same transport,
  but the three audited failures are caught and re-raised as a
  `ConnectorError` with a sentence written for the next turn, not a human
  reading a log.

## Step 1 & 2: trigger the three errors, read them exactly as the agent would

### Invalid credentials (401) — live

```python
connector_before.get_file("asadullah48", "crash-course", "README.md",
                           token="ghp_this_is_not_a_real_token_0000000000")
```

```
EXCEPTION TYPE: HTTPError
str(e): HTTP Error 401: Unauthorized
```

That's the entire message an agent gets by default — `str(e)` on the
exception, which is all a naive catch-and-log would ever show. Nothing in
it says what's wrong with the token or what to do about it.

**The wasted beat, demonstrated, not asserted:** a naive agent with only
that message to go on has no reason to change anything before retrying.
So the identical call was retried, unchanged, on purpose:

```
RETRY, SAME CALL -> still: HTTP Error 401: Unauthorized
```

Same failure. That retry is the beat this project is about — one full
turn spent, and nothing learned, because the error never told the agent
what to change.

### Missing file (404) — live

```python
connector_before.get_file("asadullah48", "crash-course",
                           "this-file-does-not-exist-drill.md")
```

```
EXCEPTION TYPE: HTTPError
str(e): HTTP Error 404: Not Found
```

Same shape of problem: true, and useless. It doesn't say the path was
wrong, doesn't suggest a real one, doesn't say where to look.

### Rate limit exceeded (403) — simulated, disclosed

Actually exhausting GitHub's real rate limit to capture this one message
means either burning the full 5000-request authenticated budget or
hammering the API unauthenticated in a tight loop hoping to trip the
secondary abuse limit. Neither is reasonable to do to a real, shared,
third-party service just for a demo, so this leg runs against
`rate_limit_drill.py`, a mock transport that reproduces GitHub's real,
documented 403 shape byte-for-byte (headers and message text both copied
from GitHub's own REST API rate-limiting docs) and feeds it through the
exact same connector code a real response would hit. `connector.py` never
knows the difference between a real socket and this mock — the code path
being exercised is the real one, only the transport is faked.

```
--- before: raw error, exactly as an agent would read it ---
str(e): HTTP Error 403: rate limit exceeded
```

Same problem again: "403" says nothing about *why*, and nothing about
*when it would be safe to try again*.

## Step 3 & 4: the rewrite

```python
if e.code == 401:
    raise ConnectorError(
        "Invalid credentials (401): the token was rejected. "
        "Get a fresh token (e.g. `gh auth token`) and retry with it, "
        "or omit the token entirely for an unauthenticated read of a "
        "public repo."
    ) from e

if e.code == 404:
    raise ConnectorError(
        f"File not found (404): '{path}' does not exist in "
        f"{owner}/{repo} on its default branch. Check the path is "
        f"correct -- list the repo root first if unsure -- then "
        f"retry with a real path."
    ) from e

if e.code == 403 and e.headers.get("X-RateLimit-Remaining") == "0":
    reset_at = int(e.headers.get("X-RateLimit-Reset", time.time()))
    wait_s = max(0, reset_at - int(time.time()))
    raise ConnectorError(
        f"Rate limit exceeded (403): 0 requests remaining. "
        f"Wait {wait_s} seconds before retrying (resets at {reset_at})."
    ) from e
```

Each message says three things: what failed, why (in plain terms), and
the exact next move. This maps directly onto the task's three examples —
"Refresh token and retry," "Create or reference a valid file path," "Wait
60 seconds before retrying" — with enough specificity added (a real
command, a real hint, a real countdown) that the next move doesn't need a
human to interpret it first.

## Step 5: update the connector, then prove the self-heal

This is the part that has to be demonstrated, not just claimed: the same
calls, run again against `connector.py`, and then — following nothing but
the rewritten message's own instruction — a genuine second attempt.

**401, rewritten:**

```
ConnectorError: Invalid credentials (401): the token was rejected. Get a
fresh token (e.g. `gh auth token`) and retry with it, or omit the token
entirely for an unauthenticated read of a public repo.
```

Acting on exactly that instruction — `gh auth token` for a fresh token,
piped straight into the retry without ever being printed — the next call:

```
SUCCESS, first line of README.md: # Crash Course Projects
```

*(An honest aside, logged rather than hidden: the first time this step
was run, the fresh token was printed to the terminal by mistake before
being piped in — a real credential briefly visible in this session's
transcript. Flagged to the user immediately; the retry above was redone
piping the token directly between commands, never displayed. Worth
carrying forward as its own lesson: "get a fresh token and retry" is easy
advice for an agent to follow badly.)*

**404, rewritten:**

```
ConnectorError: File not found (404): 'this-file-does-not-exist-drill.md'
does not exist in asadullah48/crash-course on its default branch. Check
the path is correct -- list the repo root first if unsure -- then retry
with a real path.
```

Retrying with a real path, per the instruction:

```
SUCCESS, first line of README.md: # Crash Course Projects
```

**403, rewritten, mocked transport:**

```
ConnectorError: Rate limit exceeded (403): 0 requests remaining. Wait 3
seconds before retrying (resets at 1787162676).
(sleeping 4s, exactly as the message said, for real)
SUCCESS after waiting out the window: # Crash Course Projects
```

That sleep is a real `time.sleep()`, not a narrated one — the script
waits out an actual clock window before the retry, so the "self-heal" is
a genuine pass/fail against wall-clock time, not a scripted success.

## The beat that used to be wasted, pointed at directly

Before the rewrite: `str(e)` says `HTTP Error 401: Unauthorized`, an
agent retries the identical call, and gets `HTTP Error 401: Unauthorized`
again. One full turn, zero new information, zero progress. That retry,
captured above word for word, **is** the wasted beat.

After the rewrite: the same failure produces a message with a concrete
next action baked in. The very next attempt is not a retry — it's the
correction — and it succeeds. The beat that used to be spent finding out
the identical thing twice is now spent fixing the actual problem once.

## What actually happened, summarized

| Error | Before (raw) | After (rewritten) | Self-heals? |
|---|---|---|---|
| 401 invalid credentials | `HTTP Error 401: Unauthorized` — retried blind, failed again | Names the fix, names the command | Yes — fresh token, real success |
| 404 missing file | `HTTP Error 404: Not Found` | Names the bad path, suggests checking the repo root | Yes — real path, real success |
| 403 rate limit (mocked, disclosed) | `HTTP Error 403: rate limit exceeded` | Names the exact wait, in seconds | Yes — real sleep, real success |

## Try it yourself

```bash
cd harness-eng/the-error-audit
py -c "import connector_before as c; c.get_file('asadullah48', 'crash-course', 'nope.md')"
py -c "import connector as c; c.get_file('asadullah48', 'crash-course', 'nope.md')"
py rate_limit_drill.py
```

Compare the first two lines. That difference is the whole project.
