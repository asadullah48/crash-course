import sys

from bug import slugify

cases = [
    ("Hello World", "hello-world"),
    ("Already-Slug", "already-slug"),
    ("UPPER CASE TITLE", "upper-case-title"),
]
failures = [(s, want, slugify(s)) for s, want in cases if slugify(s) != want]

if failures:
    for s, want, got in failures:
        print(f"slugify({s!r}) = {got!r}, want {want!r}")
    sys.exit(1)

print("all slugify cases passed")
sys.exit(0)
