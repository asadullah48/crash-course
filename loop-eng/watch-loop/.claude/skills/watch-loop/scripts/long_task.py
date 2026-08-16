#!/usr/bin/env python3
"""The long-running task the watch loop keeps an eye on.

Simulates real work (a batch job, a build, a render — anything that takes
minutes, not seconds) by sleeping, then writes a status file so a separate
process can tell it is done without asking the task itself.

Usage:
    python3 long_task.py [--seconds N] [--items N]
"""
import argparse
import json
import os
import time
from datetime import datetime, timezone

STATUS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".task")
STATUS_PATH = os.path.join(STATUS_DIR, "status.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=90, help="how long the task takes")
    parser.add_argument("--items", type=int, default=42, help="fake units of work to report")
    args = parser.parse_args()

    os.makedirs(STATUS_DIR, exist_ok=True)

    # Mark the task as running so a checker can distinguish "not started yet"
    # from "started, still going" from "finished" — three real states, not two.
    started_at = datetime.now(timezone.utc).isoformat()
    _write_status({"status": "running", "started_at": started_at, "pid": os.getpid()})
    print(f"[long_task] started - will finish in {args.seconds}s - pid={os.getpid()}")

    time.sleep(args.seconds)

    finished_at = datetime.now(timezone.utc).isoformat()
    _write_status(
        {
            "status": "done",
            "started_at": started_at,
            "finished_at": finished_at,
            "items_processed": args.items,
            "pid": os.getpid(),
        }
    )
    print(f"[long_task] finished - processed {args.items} items")


def _write_status(payload: dict) -> None:
    # Write to a temp file and rename over the real one. A watcher polling
    # status.json must never see a half-written JSON file - os.replace() on
    # both POSIX and Windows swaps the file in one atomic step.
    tmp_path = STATUS_PATH + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp_path, STATUS_PATH)


if __name__ == "__main__":
    main()
