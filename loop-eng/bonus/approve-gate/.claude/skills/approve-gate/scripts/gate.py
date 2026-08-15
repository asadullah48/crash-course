#!/usr/bin/env python3
"""gate.py — a loop that stops and waits for a human before it deletes anything.

Every other project in this course only ever READS the world: fetch a
position, fetch papers, fetch a status code. This one can WRITE -- it deletes
files -- and deleting is the one kind of action a loop must never take
unattended. So this script has a hard rule built in, not just documented: it
always shows its plan first, and only ever deletes when you pass --approve
explicitly. There is no other way to make it delete anything.

    python3 gate.py --setup     # first time only: build a messy sandbox/ to clean up
    python3 gate.py             # DRY RUN -- shows the plan, deletes nothing
    python3 gate.py --approve   # actually deletes what the plan showed
    python3 gate.py --json      # the plan as data, no side effects

Everything this script ever touches lives inside sandbox/, next to this
file. It will not look anywhere else, on purpose.
"""

import argparse, json, os, sys, time

# Windows terminals often default stdout to cp1252, which can't encode the emoji
# below and would crash a loop on its own display. Force UTF-8 so that never happens.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
SANDBOX = os.path.join(HERE, "sandbox")   # the ONLY directory this script will ever touch
STALE_EXTENSIONS = (".tmp", ".log", ".bak")
STALE_AFTER_DAYS = 14

SETUP_FILES = [
    # (name, age_in_days, size_bytes) -- a mix of stale junk and things that must survive
    ("build.log",         40, 1200),
    ("session.tmp",       25,  300),
    ("crash-2026-01.log", 33,  900),
    ("old-render.bak",    60, 4096),
    ("today.log",          0,  150),   # too fresh -- must NOT be deleted
    ("notes.md",           90,  500),  # not a junk extension -- must NEVER be deleted
    ("keep.tmp",            3,  200),  # a .tmp, but too fresh -- must NOT be deleted yet
]


def setup():
    """Build a synthetic messy folder to clean up. Safe to re-run -- it just resets sandbox/."""
    os.makedirs(SANDBOX, exist_ok=True)
    now = time.time()
    for name, age_days, size in SETUP_FILES:
        path = os.path.join(SANDBOX, name)
        with open(path, "w") as f:
            f.write("x" * size)
        stamp = now - age_days * 86400
        os.utime(path, (stamp, stamp))   # back-date it, so age is real, not simulated
    print(f"  built {len(SETUP_FILES)} files in {SANDBOX}/ -- some old, some new, on purpose.")
    print("  run `python3 gate.py` next to see the cleanup plan (nothing is deleted yet).")


def scan():
    """Return every file with its stale/keep verdict. Never deletes -- read-only."""
    if not os.path.isdir(SANDBOX):
        print(f"No {SANDBOX}/ yet. Run `python3 gate.py --setup` first.")
        sys.exit(1)
    now = time.time()
    plan = []
    for name in sorted(os.listdir(SANDBOX)):
        path = os.path.join(SANDBOX, name)
        if not os.path.isfile(path):
            continue
        age_days = (now - os.path.getmtime(path)) / 86400
        stale = name.lower().endswith(STALE_EXTENSIONS) and age_days >= STALE_AFTER_DAYS
        plan.append({"name": name, "age_days": round(age_days, 1),
                      "size": os.path.getsize(path), "stale": stale})
    return plan


def show_plan(plan):
    to_delete = [f for f in plan if f["stale"]]
    kept = [f for f in plan if not f["stale"]]

    print()
    print(f"  \U0001F6AA  APPROVE GATE  ·  {SANDBOX}")
    print("  " + "-" * 60)
    if not to_delete:
        print("     nothing matches the stale rule -- nothing to clean.")
    else:
        for f in to_delete:
            print(f"     - {f['name']:<20} {f['age_days']:>6.1f}d old   {f['size']:>6,}B")
        total = sum(f["size"] for f in to_delete)
        print(f"     {len(to_delete)} file(s), {total:,} bytes would be deleted.")
    if kept:
        print(f"     ({len(kept)} file(s) kept: wrong extension, or under {STALE_AFTER_DAYS}d old)")
    print("  " + "-" * 60)
    return to_delete


def main():
    parser = argparse.ArgumentParser(description="Show, then optionally run, a cleanup plan.")
    parser.add_argument("--setup", action="store_true", help="build the sandbox to clean up")
    parser.add_argument("--approve", action="store_true", help="actually delete the planned files")
    parser.add_argument("--json", action="store_true", help="print the plan as JSON, no side effects")
    args = parser.parse_args()

    if args.setup:
        setup()
        return

    plan = scan()

    if args.json:
        print(json.dumps(plan, indent=2))
        return

    to_delete = show_plan(plan)

    if not to_delete:
        return

    if not args.approve:
        print("   DRY RUN -- nothing was deleted. Re-run with --approve to actually delete these.")
        print()
        return

    for f in to_delete:
        os.remove(os.path.join(SANDBOX, f["name"]))
    print(f"   ✓ deleted {len(to_delete)} file(s). That only happened because --approve was passed.")
    print()


if __name__ == "__main__":
    main()
