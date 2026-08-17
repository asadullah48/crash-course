#!/usr/bin/env python3
"""Check whether the long-running task has finished.

Exit code doubles as the signal a shell loop polls on:
    0 -> done
    1 -> still running (or not started yet)

Usage:
    python3 check_status.py [--quiet]
"""
import argparse
import json
import os
import sys

STATUS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".task", "status.json")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="exit code only, no output")
    args = parser.parse_args()

    if not os.path.exists(STATUS_PATH):
        if not args.quiet:
            print("[check_status] not started yet")
        return 1

    with open(STATUS_PATH) as f:
        status = json.load(f)

    if status.get("status") != "done":
        if not args.quiet:
            print(f"[check_status] still running (started {status.get('started_at')})")
        return 1

    if not args.quiet:
        print(
            f"[check_status] DONE - finished {status['finished_at']} - "
            f"processed {status['items_processed']} items"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
