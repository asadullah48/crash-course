# The Flaky Line — a loop that expects to fail

**Bonus project — retry loops (error recovery).**

Every project so far calls something and trusts it to answer. Real APIs do not always answer.
This one calls a public endpoint that is *designed* to fail some of the time, and makes visible
the part every other script in this course hides inside a `for attempt in range(1, TRIES + 1)`
loop: the retries, the backoff, and the moment it has to admit defeat.

## Run it

```bash
git clone https://github.com/panaversity/agentfactory-labs.git
cd agentfactory-labs/crash-course/loop-eng/bonus/flaky-line
claude
```

Say **yes** when Claude asks whether you trust the folder. Then ask:

```
call the flaky endpoint and show me the retry log
```

You'll see each attempt, live:

```
  🔌  FLAKY LINE  ·  codes=200,200,200,500,503  ·  up to 5 attempts
  ------------------------------------------------------------
   attempt 1/5  ->  HTTP 500
      -> failed, waiting 1.2s before retrying
   attempt 2/5  ->  HTTP 200  ✓
  ------------------------------------------------------------
   ✓ succeeded on attempt 2/5
```

## Make it fail on purpose

The default mix mostly succeeds, so try the version that never does:

```
call the flaky endpoint but force it to always fail, and tell me what happens
```

That runs `--codes 500,503` — every attempt fails, the delays get longer each time
(1s, then ~2s, then ~4s...), and after 5 attempts it stops and says so:

```
   ✗ gave up after 5 attempts -- every one failed.
     This is not a bug. A retry loop that always eventually 'succeeds' is lying --
     sometimes the honest answer is 'it did not work,' loudly, and then it stops.
```

That message is the whole project. A retry loop is not "never fail" — it is "fail honestly,
after trying reasonably hard."

## How this differs from the retries you've already seen

`iss.py` and `paperwatch.py` both retry quietly — 3 tries, a short fixed pause, then give up.
That is the right amount of ceremony for *their* job: the retry is a safety net, not the point.

Here the retry loop **is** the point, so it is loud instead of quiet: every attempt prints, every
wait is shown, and the backoff *grows* (exponential, not fixed) so a real struggling server gets
breathing room instead of a hammering. That is the difference between "retry a couple of times as
an afterthought" and "build a retry loop on purpose."

## What it ships

| File                                        | Job                                                                |
| -------------------------------------------- | ------------------------------------------------------------------- |
| `.claude/skills/flaky-line/`                 | Owns the calling, the backoff timing, and the honest give-up        |
| `.claude/skills/flaky-line/scripts/flakyline.py` | Calls httpbin.org's random-status endpoint; never fakes success |
| `.claude/settings.json`                      | Three narrow pre-granted rules: the skill, the script, `httpbin.org` |
| `AGENTS.md`                                  | Points any agent at the skill/script — read by every agent          |
| `CLAUDE.md`                                  | One line — imports `AGENTS.md` so Claude Code reads it too          |

## Rate limits

`httpbin.org` is a shared public test service — fine for occasional runs, but avoid hammering it in
a tight loop from a classroom-sized group at once.
