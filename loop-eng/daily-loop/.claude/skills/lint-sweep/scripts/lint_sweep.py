#!/usr/bin/env python3
"""lint_sweep.py — Project 8's daily chore: keep our own loop-eng projects
ruff-clean, on a schedule, unattended.

Reuses Project 7's spine + harness-log pattern exactly (SPINE, LOG,
read_spine/write_spine, log_beat/mark_failure) — see
loop-eng/break-it-on-purpose/ for where that pattern was built and proven,
bug fix and all. Nothing about that pattern changes here.

THE SIX PARTS, and where each one actually lives (this script is only two
of them — the rest are the calling agent's job, described in SKILL.md):

    1. Heartbeat     -> a daily cron routine (see README.md) starts a fresh
                        agent once a day.
    2. Worktree      -> the calling agent creates an isolated worktree
                        BEFORE running this script (SKILL.md, step 1).
    3. Skill         -> SKILL.md, which wraps this script.
    4. Maker-checker -> run_maker() calls `ruff check --fix` (the maker);
                        run_checker() re-runs `ruff check` with no --fix
                        (the checker, a real command grading a real command
                        — the same discipline as Project 4's fix-loop).
    5. Connector     -> NOT this file's job. If this script exits 2 (fixed
                        and clean), the calling agent commits, pushes, and
                        opens a PR (SKILL.md, step 3). This script never
                        touches git remotes.
    6. Spine         -> read_spine()/write_spine() + log_beat()/
                        mark_failure(), identical contract to Project 7.

    python3 loop-eng/daily-loop/.claude/skills/lint-sweep/scripts/lint_sweep.py
    # ^ run from the REPO ROOT (a worktree's root), not this project's own
    #   folder -- this loop audits the whole repo, per scope.txt.

EXIT CODES (what the calling agent should do with each):
    0 = nothing to fix, loop stays quiet, no PR.
    2 = found issues, fixed them, checker confirms clean -> open a PR.
    1 = issues remain that ruff can't auto-fix -> NEEDS HUMAN, no PR.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

PROJECT_DIR = "loop-eng/daily-loop"  # this script audits the WHOLE repo, so unlike
# Project 7's brief.py, it must run from the REPO ROOT (a worktree's root) --
# its own spine/log/scope files live under here, not next to the script.
SPINE = f"{PROJECT_DIR}/progress.md"
LOG = f"{PROJECT_DIR}/loop.log"
SCOPE = f"{PROJECT_DIR}/scope.txt"


# ══════════════════════════════════════════════════════════════════════════
#  THE SPINE — identical contract to break-it-on-purpose/brief.py
# ══════════════════════════════════════════════════════════════════════════

def read_spine():
    if not os.path.exists(SPINE):
        return ""
    text = open(SPINE, encoding="utf-8").read()
    idx = text.find("\n## ")
    return text[idx + 1 :] if idx != -1 else ""


def write_spine(prior_entries, new_entry):
    header = [
        "# progress.md — the SPINE (this loop's memory)",
        "# One entry per beat: what the lint sweep found, fixed, or needs a",
        "# human for. Append-only, same discipline as every other project's spine.",
        "",
    ]
    text = "\n".join(header) + "\n" + prior_entries + new_entry
    open(SPINE, "w", encoding="utf-8").write(text)


# ══════════════════════════════════════════════════════════════════════════
#  OBSERVABILITY — identical contract to break-it-on-purpose/brief.py
# ══════════════════════════════════════════════════════════════════════════

def log_beat(status, detail=""):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    line = f"{now}  status={status}"
    if detail:
        line += f"  detail={detail}"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def mark_failure(reason):
    log_beat("FAILED", detail=f"{reason} — NEEDS HUMAN")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    prior = read_spine()
    entry = f"## {now}\n\n**FAILED — NEEDS HUMAN.** {reason}\n\n\n"
    write_spine(prior, entry)
    print(f"\n  🚨  BEAT FAILED — NEEDS A HUMAN: {reason}\n", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════════════
#  SCOPE — an allowlist, not "everything git can see". See scope.txt.
# ══════════════════════════════════════════════════════════════════════════

def read_scope():
    if not os.path.exists(SCOPE):
        return []
    paths = [
        line.strip()
        for line in open(SCOPE, encoding="utf-8")
        if line.strip() and not line.startswith("#")
    ]
    missing = [p for p in paths if not os.path.isdir(p)]
    if missing:
        raise FileNotFoundError(f"scope.txt lists missing director{'y' if len(missing)==1 else 'ies'}: {', '.join(missing)}")
    return paths


# ══════════════════════════════════════════════════════════════════════════
#  MAKER — ruff --fix. CHECKER — ruff again, no --fix. Two separate calls,
#  on purpose: the maker never gets to grade its own work.
# ══════════════════════════════════════════════════════════════════════════

def _ruff_json(paths, fix):
    cmd = ["ruff", "check", *paths, "--output-format=json"]
    if fix:
        cmd.append("--fix")
    result = subprocess.run(cmd, capture_output=True, text=True)
    # ruff exits 1 when it finds (unfixed) issues -- not a tool failure.
    if result.returncode not in (0, 1):
        raise RuntimeError(f"ruff itself failed: {result.stderr.strip()}")
    return json.loads(result.stdout or "[]")


MAX_ISSUES = 50  # blast-radius cap (Concept 5: always cap a loop -- max tries,
# max minutes, OR max spend). Not a token-cost cap; a "how much unattended
# auto-editing is this loop allowed to do in one beat" cap. A count this high
# almost certainly means scope.txt grew unexpectedly or a huge file landed --
# exactly the kind of surprise a human should look at, not the loop.


def run_maker(paths):
    """The maker: auto-fix what ruff can fix. Returns (before_count, issues_fixed).
    Refuses to touch anything if before_count exceeds MAX_ISSUES -- caller
    checks for this via the raised OverflowError before any file is touched."""
    before = _ruff_json(paths, fix=False)
    if not before:
        return 0, 0
    if len(before) > MAX_ISSUES:
        raise OverflowError(f"{len(before)} issues found, over the {MAX_ISSUES}-issue cap")
    _ruff_json(paths, fix=True)  # mutates files on disk
    after = _ruff_json(paths, fix=False)
    return len(before), len(before) - len(after)


def run_checker(paths):
    """The checker: a fresh ruff read, no --fix. Returns the remaining issues,
    exactly as a human reviewer would see them -- not the maker's opinion of
    its own work."""
    return _ruff_json(paths, fix=False)


# ══════════════════════════════════════════════════════════════════════════
#  the loop, one beat: READ the spine -> do the work -> WRITE the spine
# ══════════════════════════════════════════════════════════════════════════

def main():
    prior_entries = read_spine()

    try:
        paths = read_scope()
        before_count, fixed_count = run_maker(paths)
    except OSError as exc:
        mark_failure(str(exc))
        sys.exit(1)
    except OverflowError as exc:
        mark_failure(str(exc))
        sys.exit(1)

    remaining = run_checker(paths)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if before_count == 0:
        print(f"  ✓  lint sweep · {now} · nothing to fix, {len(paths)} dir(s) clean")
        entry = f"## {now}\n\nNothing to fix. {len(paths)} director{'y' if len(paths)==1 else 'ies'} clean.\n\n\n"
        write_spine(prior_entries, entry)
        log_beat("OK", detail="clean, no fixes needed")
        sys.exit(0)

    if remaining:
        detail = "; ".join(f"{r['filename']}:{r['location']['row']} {r['code']}" for r in remaining[:5])
        mark_failure(f"{len(remaining)} issue(s) ruff could not auto-fix: {detail}")
        sys.exit(1)

    print(f"  🔧  lint sweep · {now} · fixed {fixed_count} issue(s), now clean")
    entry = (
        f"## {now}\n\n"
        f"Fixed {fixed_count} lint issue(s) across {len(paths)} director"
        f"{'y' if len(paths)==1 else 'ies'}. Checker confirms clean. Ready for a PR.\n\n\n"
    )
    write_spine(prior_entries, entry)
    log_beat("OK", detail=f"fixed {fixed_count} issue(s), clean, PR pending")
    sys.exit(2)


if __name__ == "__main__":
    main()
