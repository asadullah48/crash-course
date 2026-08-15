#!/usr/bin/env python3
"""budgetwatch.py — a loop that watches its OWN budget, not just the world.

Every other watch in this course (sky-watch, paper-watch, iss-loop) assumes
it can call its API as often as it likes. Real APIs disagree: GitHub's
unauthenticated REST API allows exactly 60 requests per hour, per IP address,
and reports the remaining balance on every single call.

This script checks that balance -- and in doing so, spends ONE of the 60
requests it is reporting on. Checking the budget is not free. That is the
whole lesson: a loop that polls "how much budget do I have left?" without
counting the poll itself will run out faster than it thinks.

    python3 budgetwatch.py                 # the budget card
    python3 budgetwatch.py --json          # raw numbers
    python3 budgetwatch.py --warn-below 20 # exit 2 once under 20% remaining (for scripts/cron)
"""

import argparse, json, sys, time
import urllib.request

API = "https://api.github.com/rate_limit"   # a public, unauthenticated, no-key endpoint
TIMEOUT = 15
TRIES = 3

# Windows terminals often default stdout to cp1252, which can't encode the emoji
# below and would crash a loop on its own display. Force UTF-8 so that never happens.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def fetch():
    """Return the API's JSON, or exit non-zero with a plain-English reason."""
    last = None
    for attempt in range(1, TRIES + 1):
        try:
            req = urllib.request.Request(API, headers={"Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001 - any failure is the same to a reader
            last = e
            if attempt < TRIES:
                time.sleep(1)
    print(f"Could not reach GitHub's rate-limit endpoint after {TRIES} tries ({last}).")
    print("Do not guess a budget -- say this beat failed.")
    sys.exit(1)


def card(rate, warn_below):
    remaining, limit = rate["remaining"], rate["limit"]
    pct = (remaining / limit * 100) if limit else 0
    reset = time.strftime("%H:%M:%S", time.localtime(rate["reset"]))
    bar_len = 30
    filled = round(bar_len * remaining / limit) if limit else 0
    bar = "█" * filled + "░" * (bar_len - filled)

    lines = [
        "",
        "  \U0001F4B3  GITHUB API BUDGET   (unauthenticated, per IP address)",
        "  " + "-" * 60,
        f"     [{bar}]  {remaining}/{limit} left  ({pct:.0f}%)",
        f"     Resets       {reset} local time",
        f"     This check spent 1 of those {limit} -- checking is not free.",
        "  " + "-" * 60,
    ]
    if pct <= warn_below:
        lines.append(f"     ⚠ below {warn_below}% -- a scheduled loop should back off now, not keep polling.")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check the live GitHub API rate-limit budget.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--warn-below", type=float, default=20,
                        help="percent remaining under which this exits 2 instead of 0 (default 20)")
    args = parser.parse_args()

    data = fetch()
    rate = data["rate"]

    if args.json:
        print(json.dumps(rate, indent=2))
    else:
        print(card(rate, args.warn_below))

    pct = (rate["remaining"] / rate["limit"] * 100) if rate["limit"] else 0
    sys.exit(2 if pct <= args.warn_below else 0)


if __name__ == "__main__":
    main()
