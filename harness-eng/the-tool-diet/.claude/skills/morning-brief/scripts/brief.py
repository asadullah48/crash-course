#!/usr/bin/env python3
"""brief.py -- the triage loop's ONE job for this project.

Adapted, byte-for-byte in logic, from loop-eng/morning-brief/.claude/skills/
morning-brief/scripts/brief.py (this repo's own "morning-triage loop," the
one Harness Engineering Part 5 names as the loop these projects harden).
The only change: `python3` -> `py`, because that is the interpreter that
actually runs on this machine (see the-lint-hook and the-error-audit for
the same substitution).

    py brief.py             # run today's brief
    py brief.py --help      # all the options

Reads progress.md first (the spine), reports only what's new since the last
run, writes progress.md last.
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SPINE = "progress.md"


def read_spine():
    if not os.path.exists(SPINE):
        return None, ""
    text = open(SPINE, encoding="utf-8").read()
    last_commit = None
    for line in text.splitlines():
        if line.startswith("last-checked-commit:"):
            last_commit = line.split(":", 1)[1].strip()
            break
    idx = text.find("\n## ")
    prior_entries = text[idx + 1 :] if idx != -1 else ""
    return last_commit, prior_entries


def write_spine(new_commit_hash, prior_entries, new_entry):
    header = [
        "# progress.md -- the SPINE (this loop's memory)",
        "# Each run reads this file first, so it reports only what changed",
        "# since the last run.",
        "",
        f"last-checked-commit: {new_commit_hash}",
        "",
    ]
    text = "\n".join(header) + "\n" + prior_entries + new_entry
    open(SPINE, "w", encoding="utf-8").write(text)


def _git(*args):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def current_head():
    code, out = _git("rev-parse", "HEAD")
    return out if code == 0 else None


def gather_commits(since, head):
    if since is None or head is None:
        return []
    code, out = _git("log", "--oneline", f"{since}..{head}")
    if code != 0 or not out:
        return []
    return out.splitlines()


def count_todos():
    code, out = _git("grep", "-nIE", "TODO|FIXME")
    if code not in (0, 1):
        return -1
    return len([line for line in out.splitlines() if line.strip()])


def show(now, first_run, commits, todo_count):
    print()
    print(f"  MORNING BRIEF - {now}")
    if first_run:
        print("      first run - establishing a baseline, nothing to compare against yet")
    elif commits:
        print(f"      {len(commits)} new commit(s) since last run")
    else:
        print("      nothing new since last run")
    print("  " + "-" * 60)
    for line in commits:
        print(f"   - {line}")
    print(f"   open TODO/FIXME comments right now: {todo_count}")
    print("  " + "-" * 60)
    print(f"   saved this to {SPINE}, so the next run remembers it.")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Write a short morning brief: commits since last run, open TODOs."
    )
    parser.parse_args()

    last_commit, prior_entries = read_spine()
    first_run = last_commit is None

    head = current_head()
    commits = gather_commits(last_commit, head)
    todo_count = count_todos()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    show(now, first_run, commits, todo_count)

    lines = [f"## {now}", ""]
    if first_run:
        lines.append(f"First run -- baseline set at commit `{(head or 'unknown')[:8]}`.")
    elif commits:
        lines.append(f"New commits since last run ({len(commits)}):")
        lines.extend(f"- {c}" for c in commits)
    else:
        lines.append("New commits since last run: none.")
    lines.append(f"Open TODO/FIXME comments in repo: {todo_count}")
    lines.append("")
    lines.append("")
    new_entry = "\n".join(lines)

    if head is not None:
        write_spine(head, prior_entries, new_entry)


if __name__ == "__main__":
    main()
