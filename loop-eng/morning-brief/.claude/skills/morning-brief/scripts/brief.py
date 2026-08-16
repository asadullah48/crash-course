#!/usr/bin/env python3
"""brief.py — a SCHEDULED loop with a SPINE (memory between runs).

Once a run, this looks at the repo and writes a short brief: which commits
landed since the LAST run, and how many TODO/FIXME comments exist right now.
How does it know what is new since last time? It reads a file first —
progress.md, the spine — and writes to it last. That file is the memory.

    python3 brief.py             # run today's brief
    python3 brief.py --help      # all the options

HOW TO READ THIS FILE (to learn the spine):
    The whole lesson is 3 steps, and you can see them at the bottom, in main():
        1. READ the spine   -> read_spine()
        2. do the work       -> gather_commits(), count_todos()
        3. WRITE the spine   -> write_spine()
    read_spine() and write_spine() ARE the lesson — they're short, read those.
    The git calls just ask the repo what changed; you do NOT need to understand
    them to understand the spine. Treat them as a black box.
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252,
    # which can't print the emoji below -- force UTF-8 output everywhere else too.

SPINE = "progress.md"  # the memory file — read first, written last


# ══════════════════════════════════════════════════════════════════════════
#  THE SPINE  —  this is the lesson. Two short functions: read it, write it.
# ══════════════════════════════════════════════════════════════════════════

def read_spine():
    """Read the memory: which commit did we last report up to, and every
    entry a prior run already wrote (empty on the first run -> no file yet
    -> no memory -> nothing to compare against)."""
    if not os.path.exists(SPINE):
        return None, ""
    text = open(SPINE, encoding="utf-8").read()
    last_commit = None
    for line in text.splitlines():
        if line.startswith("last-checked-commit:"):
            last_commit = line.split(":", 1)[1].strip()
            break
    # Every past entry starts with "## " -- keep that whole block verbatim so
    # old entries are never rewritten, only ever added to.
    idx = text.find("\n## ")
    prior_entries = text[idx + 1 :] if idx != -1 else ""
    return last_commit, prior_entries


def write_spine(new_commit_hash, prior_entries, new_entry):
    """Write the memory: the new bookmark commit, plus every entry -- the
    ones earlier runs wrote, and the one this run just added."""
    header = [
        "# progress.md — the SPINE (this loop's memory)",
        "# Each run reads this file first, so it reports only what changed",
        "# since the last run. Delete it and the next run starts over from",
        "# scratch, as if no run had ever happened before.",
        "",
        f"last-checked-commit: {new_commit_hash}",
        "",
    ]
    text = "\n".join(header) + "\n" + prior_entries + new_entry
    open(SPINE, "w", encoding="utf-8").write(text)


# ══════════════════════════════════════════════════════════════════════════
#  THE BORING PART  —  ask git what changed. You can SKIP reading this; all
#  you need to know is: gather_commits(since) -> list of new commits.
# ══════════════════════════════════════════════════════════════════════════

def _git(*args):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def current_head():
    code, out = _git("rev-parse", "HEAD")
    if code != 0:
        return None
    return out


def gather_commits(since, head):
    """Commits between the last bookmark and HEAD -- empty list on a first
    run, since there is nothing yet to compare against."""
    if since is None or head is None:
        return []
    code, out = _git("log", "--oneline", f"{since}..{head}")
    if code != 0 or not out:
        return []
    return out.splitlines()


def count_todos():
    """How many TODO/FIXME comments exist in the repo right now."""
    code, out = _git("grep", "-nIE", "TODO|FIXME")
    if code not in (0, 1):  # git grep exits 1 for "no matches" -- not an error
        return -1
    return len([line for line in out.splitlines() if line.strip()])


# ══════════════════════════════════════════════════════════════════════════
#  showing the result on screen
# ══════════════════════════════════════════════════════════════════════════

def show(now, first_run, commits, todo_count):
    print()
    print(f"  🌅  MORNING BRIEF  ·  {now}")
    if first_run:
        print("      first run — establishing a baseline, nothing to compare against yet")
    elif commits:
        print(f"      {len(commits)} new commit(s) since last run")
    else:
        print("      nothing new since last run  ✓")
    print("  " + "-" * 60)
    for line in commits:
        print(f"   • {line}")
    print(f"   open TODO/FIXME comments right now: {todo_count}")
    print("  " + "-" * 60)
    print(f"   saved this to {SPINE}, so tomorrow's run remembers it.")
    print()


# ══════════════════════════════════════════════════════════════════════════
#  the loop, one beat:   READ the spine  ->  do the work  ->  WRITE the spine
# ══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Write a short morning brief: commits since last run, open TODOs."
    )
    parser.parse_args()

    # 1. READ THE SPINE — what did the last run already report up to?
    last_commit, prior_entries = read_spine()
    first_run = last_commit is None

    # 2. DO THE WORK — gather only what is new since the bookmark.
    head = current_head()
    commits = gather_commits(last_commit, head)
    todo_count = count_todos()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    show(now, first_run, commits, todo_count)

    # 3. WRITE THE SPINE — move the bookmark to HEAD and append today's entry,
    #    so the NEXT run starts from here instead of reporting all this again.
    lines = [f"## {now}", ""]
    if first_run:
        lines.append(f"First run — baseline set at commit `{(head or 'unknown')[:8]}`.")
    elif commits:
        lines.append(f"New commits since last run ({len(commits)}):")
        lines.extend(f"- {c}" for c in commits)
    else:
        lines.append("New commits since last run: none.")
    lines.append(f"Open TODO/FIXME comments in repo: {todo_count}")
    lines.append("")
    new_entry = "\n".join(lines)

    if head is not None:
        write_spine(head, prior_entries, new_entry)


if __name__ == "__main__":
    main()
