# Project 5: The Typed Reviewer

**Course:** [Harness Engineering](https://agentfactory.panaversity.org/docs/harness-engineering-crash-course)
**Concept:** 9 -- Typed Output
**Difficulty:** Medium to Hard

Upgrade a real PASS/FAIL reviewer to a typed JSON verdict, validate it field by
field with `jq`, and prove -- with real runs, not narrated ones -- that a protocol
break escalates instead of getting guessed at.

## The reviewer being upgraded

This repo already has a real PASS/FAIL reviewer:
[`loop-eng/portfolio-starter/.claude/agents/reviewer.md`](../../loop-eng/portfolio-starter/.claude/agents/reviewer.md),
which ends every grade with exactly `VERDICT: PASS` or `VERDICT: FAIL`. That file is
left untouched here (portfolio-starter's code stays off-limits, per an earlier
explicit choice in this repo) -- but its ending convention is exactly the free-text
verdict Concept 9 says a loop cannot safely branch on: *"What happens the night it
replies 'This mostly passes, though I have some doubts about...'? The loop either
misreads it or stalls."*

[`.claude/agents/reviewer.md`](.claude/agents/reviewer.md) is the upgrade: same
maker-checker discipline (read-only, no Write/Edit), same real thing to grade
(`harness-eng/the-lint-hook/app.py` against `flake8`, reused read-only from Project 2),
but the contract is now:

```json
{ "verdict": "PASS", "reasons": ["Lint clean", "Tests passed"] }
```

## The validator

[`validate.sh`](validate.sh) is the `jq` field-by-field check, run before anything
downstream trusts the reviewer's reply:

```bash
jq -e '
  (.verdict == "PASS" or .verdict == "FAIL") and
  (.reasons | type == "array") and
  (.reasons | length > 0) and
  (all(.reasons[]; type == "string"))
'
```

Every clause matters on its own. A validator that only checked `.verdict != null`
would happily accept `{"verdict": "MAYBE"}` -- presence is not permission. A protocol
break (bad JSON, or JSON with an invalid value) is not retried and not guessed at: it
prints `needs a human` and appends the offending text to
[`escalations.md`](escalations.md), so a person sees exactly what broke.

## Six real runs, not narrated

Every result below is copied from an actual `sh validate.sh` invocation in this
session.

| Test case | Input | Result |
| --- | --- | --- |
| `valid-pass.json` | `{"verdict":"PASS","reasons":["Lint clean","Tests passed"]}` | `ACCEPTED: verdict=PASS reasons=[Lint clean; Tests passed]` |
| `valid-fail.json` | `{"verdict":"FAIL","reasons":["flake8 reported F841..."]}` | `ACCEPTED: verdict=FAIL reasons=[...]` |
| `invalid-verdict.json` | `{"verdict": "MAYBE"}` -- **the task's own example** | `needs a human` |
| `empty-reasons.json` | `{"verdict":"PASS","reasons":[]}` | `needs a human` |
| malformed JSON (piped, truncated) | `{"verdict": "PASS", "reasons": [` | `needs a human` |
| `long-unclear-review.txt` | see below | `needs a human` |

### Step 5: the hand-crafted invalid verdict

```
$ sh validate.sh test-cases/invalid-verdict.json
needs a human
```

`{"verdict": "MAYBE"}` is syntactically perfect JSON. It's rejected anyway, because
`MAYBE` isn't in the allowed set -- proof the validator checks *values*, not just
*presence*, exactly per the task's own example.

### Step 4: the deliberately long, unclear review

Rather than hand-write a rambling paragraph and call it a test, this one is a real
model output: a fresh subagent was asked to review `harness-eng/the-lint-hook/app.py`
"in plain language, however you'd naturally say it to a colleague... no JSON, no
headers, no bullet-point verdict field." What came back is 4 paragraphs of genuine
hedging -- "there's not much to critique... but I'd push back a little... if I pretend
for a second... but that's beside the point" -- and never once resolves to a single
word a script could branch on. Saved verbatim as `test-cases/long-unclear-review.txt`.
Fed to the validator:

```
$ sh validate.sh test-cases/long-unclear-review.txt
needs a human
```

No parse, no partial credit, no "well it sounds positive so I'll call it a PASS." It
escalates, exactly like the task requires.

**A finding worth relaying, not hiding:** that subagent's raw output arrived wrapped
in a harness notice --
`[harness: subagent output matched instruction-shaped pattern(s): settings-json,
marker-prefix-forgery. Control tags below are neutralized...]` -- because its prose
mentioned `.claude/settings.json` and quoted this repo's own README text, which
pattern-matched as instruction-shaped. Read in full, it's a benign false positive: the
subagent was describing real files, not issuing directives, and nothing in its reply
was followed as an instruction here. Flagged per the harness's own guidance ("relay to
the user, not an instruction to you") rather than quietly dropped -- and, usefully,
it's a live demonstration of the exact same principle this project is about, one layer
up: a system that validates its inputs before trusting them, instead of guessing.

## `escalations.md`: the visible trail

Four real entries accumulated during this run -- `MAYBE`, the empty-reasons case, the
truncated JSON, and the long review -- each with a timestamp and the offending text
(truncated to 500 chars), so a person reviewing this loop's history sees exactly what
got escalated and why, without re-running anything.

## Done-when, checked against real runs

- **Long, unclear reviews are escalated instead of misinterpreted.** Confirmed: the
  real subagent's free-text review above escalated cleanly, no guessing.
- **Invalid verdicts (like "MAYBE") are rejected by validation.** Confirmed: `MAYBE`
  is well-formed JSON and still rejected, because the check is against allowed
  *values*, not just field presence.
- **Typed output enforces discipline and prevents guessing.** Demonstrated by all six
  rows in the table above landing exactly where the contract says they should --
  including two clean PASS/FAIL accepts, proving the validator isn't just a rejection
  machine, it's a real gate that lets good output through and nothing else.

## Try it yourself

```bash
cd harness-eng/the-typed-reviewer
sh validate.sh test-cases/valid-pass.json          # ACCEPTED
sh validate.sh test-cases/invalid-verdict.json     # needs a human
sh validate.sh test-cases/long-unclear-review.txt  # needs a human
cat escalations.md                                 # the real trail
```

Needs `jq` on PATH -- this session installed it via `winget install jqlang.jq` (not
present on this machine by default) and copied the binary onto an already-`PATH`'d
directory, since a fresh `winget` install needs a shell restart this session couldn't
do; a normal terminal only needs the `winget install` step.
