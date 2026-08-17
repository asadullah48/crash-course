# The Doorbell Loop — checkpoint, paused mid-setup

**Loop Engineering, Concept 7 (event-driven) + Concept 10 (connectors).**

**Status: SETUP COMPLETE, verification pending.** `/install-github-app` was
retried in a later session and succeeded: `CLAUDE_CODE_OAUTH_TOKEN` now exists
as a repo secret, and the installer pushed `.github/workflows/claude-code-review.yml`
(PR-triggered, no prompt needed) + `.github/workflows/claude.yml` (`@claude`
mention-triggered, bonus/not required for this project) on a separate branch
(`add-claude-github-actions-1786953102351`), with no PR opened for it.

Those two files were copied onto this branch in place of the hand-copied
`doorbell.yml`, which is now deleted — the installer's `claude-code-review.yml`
covers the same `pull_request` trigger (plus `ready_for_review`/`reopened`) and
is the maintained, official version, so keeping both would have fired two
redundant reviews per PR event. See "What actually happened this session" below
for the original blocked attempt; the "Resume from here" section has been
updated to reflect what's left: steps 1-3 are done, 4-8 (plant a bug, watch it
fire twice) are still open.

## The goal

Make this repo review its own pull requests automatically, with no prompt typed:
plant a bug in a PR, watch an unrequested review appear, then push a commit
(`synchronize`) and watch it fire again — proving the event heartbeat.

## What actually happened this session

1. **Tried Claude Code's native Routines + GitHub trigger first** (the `/schedule`
   `RemoteTrigger` API, real access confirmed). **Blocked**: linking GitHub to the
   routine kept redirecting to `claude.ai/admin-settings/claude-code/github`, which
   returned "You don't have access to organization settings" — twice, on two
   different entry points. This account appears to sit under a Claude organization
   that gates GitHub sync behind an Owner. Not something either of us could push
   through without that Owner's involvement.

2. **Pivoted to the GitHub Actions path** (`/install-github-app`), which only needs
   *repo* admin access (which the account has), not claude.ai org-Owner rights:
   - Ran `/install-github-app` from a separate `claude` terminal session.
   - GitHub App install screen: chose the **asadullah48** account (not the
     `developer-networking` org — wrong owner for this repo) and **"Only select
     repositories" → crash-course** (least-privilege, not "All repositories").
   - Reviewed and accepted the permission set (contents, issues, PRs,
     actions/checks/workflows — read+write; commit statuses/metadata — read).
   - **Stopped here**: the install step returned *"Claude is temporarily
     unavailable — we're working on it — try again in a moment."* This is a
     transient error on Anthropic's infrastructure, not a configuration mistake.

3. **Verified via `gh` what actually landed so far** (from this session, not the
   `/install-github-app` session): **no** `CLAUDE_CODE_OAUTH_TOKEN` /
   `ANTHROPIC_API_KEY` secret exists yet on the repo (`gh secret list` is empty),
   and **no** workflow-install PR has appeared (`gh pr list` shows only the five
   from Projects 1-4). So the GitHub App may or may not have finished installing,
   but the token + workflow half of the setup has not happened.

## What's staged but NOT committed to this state

On branch `add-doorbell-workflow`, copied from the repo's existing
[`loop-eng/doorbell/`](../doorbell/) kit, sitting at the actual repo root (required
-- GitHub only evaluates `pull_request`-triggered workflows from files on the PR's
base branch, never from a subfolder):

- `.github/workflows/doorbell.yml` -- the hand-authored workflow from the existing
  kit (`pull_request: [opened, synchronize]` -> `anthropics/claude-code-action@v1`
  with `track_progress: true`)
- `readings.py` -- the file the kit uses as something to review

**These may be redundant with, or need reconciling against, whatever
`/install-github-app` generates** once its own flow completes (it may write its own
`claude-code-review.yml` using a different secret name or trigger shape). Don't
assume this hand-copied file is the final answer -- compare the two once the
official flow finishes, and keep only one.

## Resume from here, next session

1. ~~Retry `/install-github-app`~~ **DONE** -- succeeded on retry, no PR was
   auto-opened but the workflow branch was pushed.
2. ~~`gh secret list` should show `CLAUDE_CODE_OAUTH_TOKEN`~~ **DONE** --
   verified present (`gh secret list --repo asadullah48/crash-course`).
3. ~~Compare workflow files, keep one, merge to `main`~~ **DONE** -- kept the
   installer's `claude-code-review.yml` (+ bonus `claude.yml`), deleted the
   hand-copied `doorbell.yml`, merged to `main` via PR.
4. **Plant one bug** in a small PR (an off-by-one, a deleted null check -- the
   existing kit's own README has a ready-made example using `readings.py`'s
   `average_altitude`).
5. **Don't type a prompt.** Just open the PR and wait. A review should appear on
   its own within a couple of minutes.
6. Push a second commit to the same PR (`synchronize`) and confirm a **second**,
   independent review fires -- that's the event heartbeat re-firing, the specific
   thing this project is testing for.
7. If the review misses the planted bug: tighten the prompt in the workflow
   (`doorbell.yml`'s `prompt:` block) and push again -- per this project's own
   "Done when," that's not a failure, that's the lesson.
8. Once verified, this closes the loop on all four heartbeats from this course:
   in-session (Project 1), conditional (Project 2), scheduled (Project 3),
   event-driven (this project).

## Why not the Routines path instead

Routines are the more modern mechanism (no workflow YAML to maintain, no repo
secret, managed entirely from `claude.ai/code/routines` or `/schedule`) and are
documented as available on Pro/Max, not just Team/Enterprise -- so this account's
org-settings block is likely specific to how this particular claude.ai account is
provisioned, not a hard plan limitation. Worth revisiting later with whoever owns
that organization; the filter table for a GitHub PR trigger (Author, Title, Body,
Base branch, Head branch, Labels, Is draft, Is merged -- each with equals /
contains / starts with / is one of / is not one of / matches regex) is documented
at [code.claude.com/docs/en/routines](https://code.claude.com/docs/en/routines) if
that path opens up.
