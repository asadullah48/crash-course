import sys

from bug import dedupe

cases = [
    ([3, 1, 2, 1, 3], [3, 1, 2]),
    ([1, 1, 1], [1]),
    ([], []),
]
failures = [(items, want, dedupe(items)) for items, want in cases if dedupe(items) != want]

if failures:
    for items, want, got in failures:
        print(f"dedupe({items}) = {got}, want {want}")
    sys.exit(1)

print("all dedupe cases passed")
sys.exit(0)
