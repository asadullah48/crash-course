#!/usr/bin/env python3
"""critic.py — the mechanical rung of a self-review loop. Python stdlib only.

This project has no "generator" script -- the generator is Claude, writing
your elevator pitch in pitch.md. This file is only the CRITIC: a fixed,
un-arguable rubric that either passes or does not. The loop is: write,
run this, read what failed, rewrite, run this again -- until every check
is green. Nobody grades their own pitch as done; this does.

    python3 critic.py             # grade pitch.md against the rubric below
    python3 critic.py mine.md     # grade a different file
    python3 critic.py --json
"""

import argparse, json, os, re, sys

# Windows terminals often default stdout to cp1252; critic.py itself prints no
# emoji, but keep this consistent with the other bonus scripts for safety.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BANNED = [
    "synergy", "synergies", "leverage", "disrupt", "paradigm shift",
    "cutting-edge", "cutting edge", "world-class", "world class",
    "passionate about", "innovative solution", "game-changer", "game changer",
    "best-in-class", "best in class", "revolutioniz",
]
GREETING_OPENER = re.compile(r"^\s*(hi|hello|hey)[,!]?\s.{0,25}\b(my name is|i'?m|i am)\b", re.I)
ASK_HINTS = ("?", "let's", "lets", "i'd love", "id love", "reach out",
             "connect with me", "email me", "get in touch", "let me know")
MIN_WORDS, MAX_WORDS = 60, 90


def load(path):
    if not os.path.exists(path):
        print(f"\n  Can't grade {path} -- it doesn't exist yet.")
        print("  Write your elevator pitch there first (see brief.md for the assignment),")
        print("  then run this again.\n")
        sys.exit(2)
    return open(path, encoding="utf-8").read().strip()


def last_sentence(text):
    # good enough for a 60-90 word pitch: split on . ! ? followed by space or end of string
    parts = [p for p in re.split(r"(?<=[.!?])\s+", text.strip()) if p]
    return parts[-1] if parts else ""


def grade(text):
    words = text.split()
    n_words = len(words)
    low = text.lower()
    hits = [b for b in BANNED if b in low]
    opener_ok = not GREETING_OPENER.match(text)
    has_number = bool(re.search(r"\d", text))
    tail = last_sentence(text)
    has_ask = any(h in tail.lower() for h in ASK_HINTS)

    return [
        (f"C1  length {MIN_WORDS}-{MAX_WORDS} words (~30s spoken)",
         MIN_WORDS <= n_words <= MAX_WORDS, f"{n_words} words"),
        ("C2  no banned buzzwords", not hits, ", ".join(hits) if hits else "clean"),
        ("C3  opens with a hook, not a greeting", opener_ok,
         "starts with a greeting" if not opener_ok else "ok"),
        ("C4  includes one concrete number or fact", has_number,
         "no digits found" if not has_number else "ok"),
        ("C5  ends with a clear ask", has_ask,
         f'last sentence: "{tail[:60]}"' if not has_ask else "ok"),
    ]


def main():
    parser = argparse.ArgumentParser(description="Grade an elevator pitch against a fixed rubric.")
    parser.add_argument("path", nargs="?", default="pitch.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = load(args.path)
    checks = grade(text)
    n_pass = sum(1 for _, ok, _ in checks if ok)

    if args.json:
        print(json.dumps({
            "path": args.path, "passing": n_pass, "total": len(checks),
            "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
        }, indent=2))
        sys.exit(0 if n_pass == len(checks) else 1)

    print(f"\n  {args.path}")
    for name, ok, detail in checks:
        print(f"  [{'x' if ok else ' '}] {name}   -> {detail}")
    print(f"\n  {n_pass}/{len(checks)} passing\n")
    sys.exit(0 if n_pass == len(checks) else 1)


if __name__ == "__main__":
    main()
