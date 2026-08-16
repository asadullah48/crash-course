#!/usr/bin/env bash
# run_fix_loop.sh -- the fix loop's BODY, codified into one re-runnable unit.
#
# For every candidate under candidates/*, in parallel, in its own isolated
# git worktree: apply that candidate's pre-authored fix, run its checker,
# record the verdict. This script is pure orchestration -- it does not
# draft fixes itself, it applies whatever fix.patch each candidate already
# ships in this repo. Swap the "DRAFT" step below for a real coding-agent
# call (`claude -p "fix candidates/$name/bug.py"`, `opencode run ...`) and
# nothing else in this script changes: the isolation, the parallelism, and
# the checker-as-gate are the reusable part.
#
# Usage:
#   ./run_fix_loop.sh
#
# This script has NO memory of any previous run. Every invocation starts
# from the same candidates/ directory and produces a fresh verdict from
# scratch -- see README.md's "prove the interlude's warning" section.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
REPO_ROOT="$(git -C "$PROJECT_ROOT" rev-parse --show-toplevel)"
CANDIDATES_DIR="$PROJECT_ROOT/candidates"
WORK_DIR="$(mktemp -d)"
RESULTS_DIR="$(mktemp -d)"
STAMP="$(date -u +%Y%m%d-%H%M%S)"

mapfile -t CANDIDATES < <(ls "$CANDIDATES_DIR")

echo "== fix loop: ${#CANDIDATES[@]} candidate(s) =="
echo "   worktrees: $WORK_DIR"
echo "   results:   $RESULTS_DIR"
echo

run_one() {
  local name="$1"
  local src="$CANDIDATES_DIR/$name"
  local wt="$WORK_DIR/$name"
  local branch="codify-body/$name-$STAMP"
  local log="$RESULTS_DIR/$name.log"

  # ISOLATE: one worktree per candidate (Concept 8) -- candidates never
  # touch each other's checkout, so they can safely run at the same time.
  if ! git -C "$REPO_ROOT" worktree add -q "$wt" -b "$branch" HEAD >"$log" 2>&1; then
    echo "WORKTREE-FAILED" > "$RESULTS_DIR/$name.verdict"
    return
  fi
  mkdir -p "$wt/work"
  cp "$src/bug.py" "$src/check.py" "$wt/work/"

  # DRAFT: apply the candidate's fix. This is the one line a real deployment
  # replaces with a coding-agent invocation -- everything else in this
  # function is the reusable engine, not the fix itself.
  if ! (cd "$wt/work" && patch -p0 < "$src/fix.patch") >>"$log" 2>&1; then
    echo "PATCH-FAILED" > "$RESULTS_DIR/$name.verdict"
    return
  fi

  # REVIEW: the checker's exit code IS the verdict -- no judgment call here,
  # just whatever `python check.py` returns.
  if (cd "$wt/work" && python check.py) >>"$log" 2>&1; then
    echo "PASS" > "$RESULTS_DIR/$name.verdict"
  else
    echo "FAIL" > "$RESULTS_DIR/$name.verdict"
  fi
}

# FAN OUT: launch every candidate's isolated attempt in the background at
# once, then block until all of them are done. This is the whole mechanism
# -- one `for`, one `&` per iteration, one `wait`.
for name in "${CANDIDATES[@]}"; do
  run_one "$name" &
done
wait

echo "== verdicts =="
exit_code=0
for name in "${CANDIDATES[@]}"; do
  verdict="$(cat "$RESULTS_DIR/$name.verdict" 2>/dev/null || echo "MISSING")"
  printf "  %-20s %s\n" "$name" "$verdict"
  [ "$verdict" = "PASS" ] || exit_code=1
done

echo
echo "worktrees left at $WORK_DIR for inspection -- clean up with (--force"
echo "because each one has an untracked patched copy of the candidate in it):"
for name in "${CANDIDATES[@]}"; do
  echo "  git -C \"$REPO_ROOT\" worktree remove --force \"$WORK_DIR/$name\""
done

exit $exit_code
