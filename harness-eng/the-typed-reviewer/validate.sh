#!/bin/sh
# validate.sh -- Concept 9, typed output. The loop validates before it believes.
#
# Usage:
#   ./validate.sh path/to/candidate-review        (file)
#   echo '{"verdict":"PASS","reasons":["ok"]}' | ./validate.sh   (stdin)
#
# Field-by-field validation, not just "does .verdict exist":
#   - verdict must be exactly "PASS" or "FAIL" (a lazier check that only asked
#     '.verdict != null' would happily accept {"verdict":"MAYBE"})
#   - reasons must be a non-empty JSON array of strings
#
# A protocol break -- malformed JSON, or JSON with an invalid value -- is not
# retried and not guessed at. It escalates: printed as "needs a human" and
# appended to escalations.md, so the loop moves on and a person sees it.

set -u
ESCALATIONS="$(dirname "$0")/escalations.md"

if [ -n "${1:-}" ]; then
  review=$(cat "$1")
else
  review=$(cat)
fi

if printf '%s' "$review" | jq -e '
  (.verdict == "PASS" or .verdict == "FAIL") and
  (.reasons | type == "array") and
  (.reasons | length > 0) and
  (all(.reasons[]; type == "string"))
' >/dev/null 2>&1
then
  verdict=$(printf '%s' "$review" | jq -r '.verdict')
  reasons=$(printf '%s' "$review" | jq -r '.reasons | join("; ")')
  echo "ACCEPTED: verdict=$verdict reasons=[$reasons]"
  exit 0
else
  echo "needs a human"
  {
    echo "- $(date -u +%Y-%m-%dT%H:%M:%SZ) reviewer output failed validation, escalated:"
    printf '  %s\n' "$review" | head -c 500
    echo
  } >> "$ESCALATIONS"
  exit 1
fi
