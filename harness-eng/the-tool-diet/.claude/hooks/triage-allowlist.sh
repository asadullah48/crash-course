#!/bin/sh
# triage-allowlist.sh -- the triage-diet agent's Bash tool may run exactly
# one command. Everything else, including the decoy manual_check.sh and any
# raw git/curl call, is rejected with a reason instead of silently allowed.
cmd=$(cat | jq -r '.tool_input.command // empty')
case "$cmd" in
  "py .claude/skills/morning-brief/scripts/brief.py"*) exit 0 ;;
  *)
    echo "Blocked: this loop's only allowed command is 'py .claude/skills/morning-brief/scripts/brief.py'. Run that instead." >&2
    exit 2
    ;;
esac
