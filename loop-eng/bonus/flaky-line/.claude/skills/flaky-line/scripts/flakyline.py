#!/usr/bin/env python3
"""flakyline.py — a loop that expects to fail, on purpose.

Every other script in this course treats a failed fetch as the end of the
line: retry a few times, then stop and say so (see iss.py, paperwatch.py).
This one is about that retry itself. It calls a public endpoint that fails
ON PURPOSE some fraction of the time, and makes the backoff visible: how
many attempts, how long each wait, and what happens when every attempt
fails anyway.

    python3 flakyline.py                    # default: mostly 200, sometimes 500/503
    python3 flakyline.py --codes 500,503    # fail every time -- watch it give up honestly
    python3 flakyline.py --codes 200        # never fails -- one attempt, done
    python3 flakyline.py --max-attempts 8 --json

HOW TO READ THIS FILE (to learn the retry loop):
    The whole lesson is in call_with_retry() -- it is short, read that first.
    request_once() just makes one HTTP call. Treat it as a black box: "ask
    for one of these status codes, get back what actually came back."
"""

import argparse, json, random, sys, time
import urllib.error, urllib.request

ENDPOINT = "https://httpbin.org/status/{codes}"   # a public web address -- no key, no login
DEFAULT_CODES = "200,200,200,500,503"             # mostly fine, sometimes not -- like a real API

# Windows terminals often default stdout to cp1252, which can't encode the emoji
# below and would crash a loop on its own display. Force UTF-8 so that never happens.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def request_once(codes, timeout=10):
    """Make exactly one call. Return (status_code, error) -- error is None on a real response."""
    req = urllib.request.Request(ENDPOINT.format(codes=codes), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, None    # a non-2xx status IS the response, not a network failure
    except Exception as e:
        return None, e         # this is a real network failure -- no status at all


# ══════════════════════════════════════════════════════════════════════════
#  THE RETRY LOOP  —  this is the lesson.
# ══════════════════════════════════════════════════════════════════════════

def call_with_retry(codes, max_attempts, base_delay=1.0, quiet=False):
    """Call the endpoint, retrying on failure with exponential backoff + jitter.

    Returns (success: bool, attempts: list of dicts) -- never raises, never lies.
    A 2xx status is success. Anything else is a failure worth retrying.
    """
    attempts = []
    for n in range(1, max_attempts + 1):
        status, error = request_once(codes)
        ok = status is not None and 200 <= status < 300
        attempts.append({"attempt": n, "status": status, "error": str(error) if error else None, "ok": ok})

        if not quiet:
            what = f"HTTP {status}" if status is not None else f"no response ({error})"
            print(f"   attempt {n}/{max_attempts}  ->  {what}" + ("  ✓" if ok else ""))

        if ok:
            return True, attempts

        if n < max_attempts:
            # exponential backoff with jitter: 1s, 2s, 4s, ... capped, plus up to 30% jitter
            # so a retry storm from many callers doesn't all retry in lock-step.
            delay = min(base_delay * (2 ** (n - 1)), 20)
            delay += random.uniform(0, delay * 0.3)
            if not quiet:
                print(f"      -> failed, waiting {delay:.1f}s before retrying")
            time.sleep(delay)

    return False, attempts


def main():
    parser = argparse.ArgumentParser(description="Call a flaky endpoint, retrying with backoff.")
    parser.add_argument("--codes", default=DEFAULT_CODES,
                        help='comma list httpbin picks from at random, e.g. --codes "500,503"')
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="print the attempt log as JSON")
    args = parser.parse_args()

    if not args.json:
        print()
        print(f"  \U0001F50C  FLAKY LINE  ·  codes={args.codes}  ·  up to {args.max_attempts} attempts")
        print("  " + "-" * 60)

    success, attempts = call_with_retry(args.codes, args.max_attempts, quiet=args.json)

    if args.json:
        print(json.dumps({"success": success, "attempts": attempts}, indent=2))
        sys.exit(0 if success else 1)

    print("  " + "-" * 60)
    if success:
        print(f"   ✓ succeeded on attempt {attempts[-1]['attempt']}/{args.max_attempts}")
        print()
        sys.exit(0)
    else:
        print(f"   ✗ gave up after {len(attempts)} attempts -- every one failed.")
        print("     This is not a bug. A retry loop that always eventually 'succeeds' is lying --")
        print("     sometimes the honest answer is 'it did not work,' loudly, and then it stops.")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
