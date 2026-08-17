# Project 9 — Prove a Prompt with One-Off Runs

*Difficulty: Easy · Uses: A1, A3 (one-off schedules), A5 (reading runs)*

The official brief (from the Loop Engineering appendix, "Practice: three routine
drills," Project 9 "Rehearse a routine for free"):

> In a throwaway repo, create a routine whose prompt does one small, checkable
> thing, for example summarizing yesterday's commits onto a `claude/summary`
> branch. Do not put it on a repeating schedule. Fire it with a one-off run
> (`/schedule tomorrow at 9am, …` or *Run now*) and read the full transcript,
> not the status column. Then change the prompt so the task must fail, by
> having it read a file that does not exist, and fire it once more.
>
> **Done when** you have seen two green runs: one whose transcript shows
> success, and one whose transcript shows failure. You should be able to say,
> in one sentence, why the status column could not tell them apart.

This repo (`asadullah48/crash-course`) is reused as the throwaway repo, same
as Projects 6 and 8 — the GitHub App is already installed here.

## The routine

One routine, `prove-a-prompt-drill` (`trig_01FrThPToEu3uAktSRbmh4kW`), fired
twice with two different prompts and never put on a recurring schedule:

1. **Run 1 — designed to succeed.** Prompt: summarize commits from the last
   24 hours onto a new `claude/summary` branch, as a file at
   `loop-eng/prove-a-prompt/summary.md`. Fired as a genuine one-off schedule
   (`run_once_at`, a few minutes in the future) — A1's "one-off schedule"
   mechanism.
2. **Run 2 — designed to fail.** The routine's prompt was edited to require
   reading a file that does not exist, then fired with `Run now` (A3's
   immediate-fire mechanism) instead of another scheduled time.

## Results

Both runs came back from `list_runs` identically: `"status": "active"`,
`"worker_status": "idle"` — the platform's own list view, the thing you'd
glance at to say "did it work?", is byte-for-byte the same for both. The
`get_run_log` transcript of each is what actually tells them apart.

| Run | Session | Trigger mechanism | List status | `result` field | Transcript verdict |
|-----|---------|--------------------|-------------|-----------------|---------------------|
| 1   | [`cse_01MSEJ5s7Hy1pvHX5rbvKGhz`](https://claude.ai/code/session_01MSEJ5s7Hy1pvHX5rbvKGhz) | one-off schedule (`run_once_at`, fired 17:37 UTC) | `active` / `idle` | `success, is_error=false` | **Real success.** Fetched `origin/main`, found 6 commits from the last 24h, created `claude/summary`, wrote `loop-eng/prove-a-prompt/summary.md` listing hash/author/subject for each, committed, and pushed. `origin/claude/summary` exists on GitHub with the real file. |
| 2   | [`cse_01HDYxfdCxjD7PN5DNqKk2zM`](https://claude.ai/code/session_01HDYxfdCxjD7PN5DNqKk2zM) | Run now (`action: "run"`, fired 17:38 UTC, same routine + edited prompt) | `active` / `idle` | `success, is_error=false` | **Real failure.** Checked out `claude/summary-fail`, tried to `Read` `loop-eng/prove-a-prompt/does-not-exist.md`, got `ERROR: File does not exist`, and correctly stopped — no file written, no commit, no push, per its own instructions not to fabricate placeholder content. `claude/summary-fail` was never pushed to origin (verified: only `origin/claude/summary` exists on the remote). |

Note the `result` field itself reads `success` on **both** runs — the platform
counts "the agent decided on its own to stop and report a failure honestly"
as the session succeeding at its job, which is a session-lifecycle judgment,
not a task judgment. That is precisely what makes the drill work: there is no
shortcut field anywhere in the API response that separates these two runs.
Reading the transcript is the only way.

## The A5 lesson

**Green (or "success," or an idle-active status row) only certifies that the
cloud session started, ran, and exited without an infrastructure failure —
it says nothing about whether the task the prompt actually asked for got
done, because both a routine that pushed real work and a routine that
correctly gave up empty-handed exit through that exact same status.**
