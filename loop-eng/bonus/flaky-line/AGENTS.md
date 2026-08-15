# The Flaky Line

This project has one job: call an endpoint that fails on purpose sometimes, and show the retry
loop -- attempts, backoff delays, and the honest outcome -- that gets it through.

**Any question about testing retries, backoff, or what happens when a call keeps failing is
answered by running this project's script, never by narrating a simulated retry:**

    python3 .claude/skills/flaky-line/scripts/flakyline.py

(In Claude Code this runs automatically through the `flaky-line` skill; any other agent should run
the script directly.) The script owns the calling, the timing, and the give-up rule.

The one thing to hold onto: sometimes every attempt fails, and the correct behaviour is to say so,
loudly, and stop. A retry loop that quietly reports success when it did not succeed is not robust
-- it is dishonest.
