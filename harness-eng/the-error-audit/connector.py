"""The AX-rewritten GitHub connector.

Same calls as connector_before.py. The only thing that changed is what a
failure hands back: instead of GitHub's raw status text, the caller gets a
sentence written for the agent that has to act on it next -- what happened,
and what to change before retrying. Same connector, same transport, so a
mocked transport (used for the rate-limit leg of the drill -- see README)
exercises the exact same code path a real 403 would.
"""

import time
import urllib.error
import urllib.request

GITHUB_API = "https://api.github.com"


class ConnectorError(Exception):
    """Raised with a message written for the agent's next turn, not a human
    reading a log after the fact."""


def get_file(
    owner: str,
    repo: str,
    path: str,
    token: str | None = None,
    _urlopen=urllib.request.urlopen,
) -> str:
    """Fetch a file's raw content from a GitHub repo.

    Raises ConnectorError with an actionable next step on the three errors
    this drill audited (401, 404, 403-rate-limit). Anything else re-raises
    the underlying HTTPError unchanged -- this rewrite only covers the
    errors that were actually audited, not a blanket catch-all.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github.raw+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with _urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise ConnectorError(
                "Invalid credentials (401): the token was rejected. "
                "Get a fresh token (e.g. `gh auth token`) and retry with it, "
                "or omit the token entirely for an unauthenticated read of a "
                "public repo."
            ) from e

        if e.code == 404:
            raise ConnectorError(
                f"File not found (404): '{path}' does not exist in "
                f"{owner}/{repo} on its default branch. Check the path is "
                f"correct -- list the repo root first if unsure -- then "
                f"retry with a real path."
            ) from e

        if e.code == 403 and e.headers.get("X-RateLimit-Remaining") == "0":
            reset_at = int(e.headers.get("X-RateLimit-Reset", time.time()))
            wait_s = max(0, reset_at - int(time.time()))
            raise ConnectorError(
                f"Rate limit exceeded (403): 0 requests remaining. "
                f"Wait {wait_s} seconds before retrying (resets at "
                f"{reset_at})."
            ) from e

        raise  # anything not audited here: let the real error through
