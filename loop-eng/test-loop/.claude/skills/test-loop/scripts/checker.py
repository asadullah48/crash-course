#!/usr/bin/env python3
"""The checker half of the maker-checker loop.

Runs pytest against sample/, tracks the attempt count, and returns one
of three exit codes -- the loop reacts to the exit code, never to its
own opinion of whether the code "looks right."

Exit codes:
    0 -> tests passed. Stop. This is success, and pytest said so.
    1 -> tests failed, attempts remain. Fix one thing and run again.
    2 -> tests failed, cap reached. Stop. This is NOT success -- if you
         keep landing here, the fix approach needs rethinking, not
         another attempt.

Usage:
    python3 checker.py [--reset] [--max-attempts N]
"""
import argparse
import json
import os
import subprocess
import sys

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
STATE_PATH = os.path.join(PROJECT_ROOT, ".attempts", "state.json")
SAMPLE_DIR = os.path.join(PROJECT_ROOT, "sample")


def _load_count() -> int:
    if not os.path.exists(STATE_PATH):
        return 0
    with open(STATE_PATH) as f:
        return json.load(f).get("attempts", 0)


def _save_count(n: int) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp_path = STATE_PATH + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump({"attempts": n}, f)
    os.replace(tmp_path, STATE_PATH)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="reset the attempt counter to 0")
    parser.add_argument("--max-attempts", type=int, default=6)
    args = parser.parse_args()

    if args.reset:
        _save_count(0)
        print("[checker] attempt counter reset")
        return 0

    attempt = _load_count() + 1
    _save_count(attempt)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", SAMPLE_DIR],
        capture_output=True,
        text=True,
    )
    print(result.stdout)

    if result.returncode == 0:
        # pytest decided this, not this script and not whoever is calling it.
        print(f"[checker] PASSED on attempt {attempt}/{args.max_attempts}")
        return 0

    if attempt >= args.max_attempts:
        print(f"[checker] CAP REACHED at {attempt}/{args.max_attempts} attempts - tests still fail.")
        print("[checker] This is not success. The fix approach needs rethinking, not another try.")
        return 2

    print(f"[checker] FAILED attempt {attempt}/{args.max_attempts} - fix and run again.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
