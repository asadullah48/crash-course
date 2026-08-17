# Project 10 — The Secrets Drill

*Difficulty: Easy to Medium · Uses: A4 (secrets), A2 (the environment)*

The official brief (Loop Engineering appendix, "Practice: three routine
drills," Project 10 "The secrets drill"):

> Write a prompt that needs one secret. A dummy token is fine, because the
> drill is about where the value lives, not what it unlocks. First run: put
> the token in a gitignored `.env` file and fire the routine. Watch it fail
> to find the value, and read the transcript to see what Claude tried
> instead. Second run: move the token into the environment-variables panel,
> and add the one prompt line the appendix recommends: *"credentials are
> available as environment variables; do not look for a `.env` file."*
>
> **Done when** the second run reads the token from the environment, and you
> can explain the mechanical reason the first run could not: gitignored
> files never reach GitHub, so the fresh cloud clone never contains them.

Same throwaway repo as Projects 6, 8, and 9 (`asadullah48/crash-course`).

## The dummy secret

`DRILL_TOKEN=dummy-token-local-only-4f9a2b` — a fabricated value, not a real
credential. It lives at `loop-eng/secrets-drill/.env`, which
`loop-eng/secrets-drill/.gitignore` excludes. Verified mechanically before
Run 1: `git check-ignore -v loop-eng/secrets-drill/.env` matches, and
`git status` never lists the file as trackable. It is therefore physically
impossible for this value to reach GitHub, let alone a fresh cloud clone —
that impossibility is the entire point of the drill.

## The routine

One routine, `secrets-drill` (`trig_01UuiRz7WLNwvRs72cUBKeu3`), fired twice
with two different prompts:

1. **Run 1 — designed to fail.** Prompt asks the routine to locate
   `DRILL_TOKEN` by any means available and report exactly how (or whether)
   it found it, writing the result to `loop-eng/secrets-drill/result.md` on
   a new `claude/secrets-drill` branch. No env var is set yet, and the
   `.env` file — real as it is on disk locally — never reaches the clone.
2. **Run 2 — designed to succeed.** Same routine, switched from the shared
   `Default` cloud environment to a new dedicated one, `secrets-drill-env`
   (created via the claude.ai web UI — `RemoteTrigger` has no API surface
   for editing an Environment's variables, only for routines that reference
   one), with `DRILL_TOKEN=dummy-token-env-panel-9c3d1e` set in its
   variables panel. The prompt gained the appendix's recommended line:
   *"Credentials are available as environment variables; do not look for a
   `.env` file."* A dedicated environment (rather than adding the variable
   to `Default`) keeps this dummy value from leaking into Project 8's real
   `daily-lint-sweep` routine, which also uses `Default`.

## Results

| Run | What changed | Transcript verdict |
|-----|--------------|---------------------|
| 1 ([`cse_01979oFUVqQYycbsAvwoRgFQ`](https://claude.ai/code/session_01979oFUVqQYycbsAvwoRgFQ)) | token only in gitignored `.env` | **Real, honest failure.** 11 turns, 220s. Checked `env`/`printenv`, searched the whole filesystem (one grep across `/` even timed out at 2 minutes and it retried narrower), read every `.gitignore` in the repo, grepped the entire git history across all branches, read both GitHub Actions workflow files, and checked every readable process's `/proc/*/environ`. Found nothing. Correctly reported "DRILL_TOKEN was not found anywhere" instead of inventing a value, and pushed `origin/claude/secrets-drill` with that honest result. |
| 2 ([`cse_01FLgAEzYUoxSonEU8as1QHq`](https://claude.ai/code/session_01FLgAEzYUoxSonEU8as1QHq)) | token in `secrets-drill-env`'s variables panel + the recommended prompt line | **Real success.** 6 turns, 23s — roughly 10x faster than Run 1, because it never touched the filesystem at all. First and only command: `env \| grep -i drill` → `DRILL_TOKEN=dummy-token-env-panel-9c3d1e`, the exact value set in the panel. Wrote `loop-eng/secrets-drill/result-success.md` and pushed `origin/claude/secrets-drill-success`. |

Verified independently of both transcripts: `git branch -r` on the real
repo shows both `origin/claude/secrets-drill` and
`origin/claude/secrets-drill-success` exist, matching each run's claim.

## The mechanical explanation

**Run 1 could not find `DRILL_TOKEN` because the value never left this
machine.** `loop-eng/secrets-drill/.env` is excluded by
`loop-eng/secrets-drill/.gitignore` (confirmed with `git check-ignore -v`
before Run 1 ever fired), so it was never `git add`-able, never committed,
and therefore never pushed to `origin/main`. A routine's cloud session
clones `origin/main` fresh on every run — it has no access to this laptop's
disk at all, gitignored or not. The file could have been sitting right next
to the routine's own generated files and it still would not have mattered:
the fresh clone is a copy of what GitHub has, and GitHub never had it. This
is also why Run 1's transcript shows it correctly *not* finding a `.env`
file to read in the first place (`loop-eng/secrets-drill/` didn't even exist
on `origin/main` yet when Run 1 fired) — it isn't "found the file, respected
the ignore rule," it's "the file was never part of the repository to begin
with." Moving the value into the environment's variables panel sidesteps
git entirely: those variables are injected into the session by the
platform itself, independent of what's in the clone, which is exactly why
Run 2 found it in one command.
