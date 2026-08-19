"""The raw GitHub connector, before the AX rewrite.

GitHub's own error text passes straight through, unmodified. This is
deliberately the naive version: whatever the API says, the caller gets,
verbatim. No interpretation, no next step. Kept as-is (not deleted) so the
before/after diff in the project README stays honest and reproducible.
"""

import urllib.error
import urllib.request

GITHUB_API = "https://api.github.com"


def get_file(owner: str, repo: str, path: str, token: str | None = None) -> str:
    """Fetch a file's raw content from a GitHub repo.

    Raises urllib.error.HTTPError on any failure, with whatever GitHub sent
    back, unmodified. The caller has to read .code and .read() themselves
    to learn anything at all.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github.raw+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode("utf-8")
