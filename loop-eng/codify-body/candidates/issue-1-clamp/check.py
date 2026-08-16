import sys

from bug import clamp_pct

cases = [(-10, 0), (0, 0), (50, 50), (100, 100), (150, 100)]
failures = [(x, want, clamp_pct(x)) for x, want in cases if clamp_pct(x) != want]

if failures:
    for x, want, got in failures:
        print(f"clamp_pct({x}) = {got}, want {want}")
    sys.exit(1)

print("all clamp_pct cases passed")
sys.exit(0)
