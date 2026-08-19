"""The rate-limit leg of the drill, run against a mocked transport.

Why mocked and not live: actually exhausting GitHub's real rate limit just
to capture one error message means either burning the full authenticated
budget (5000 requests) or hammering the API unauthenticated in a tight
loop to try to trip the secondary abuse limit -- neither is a reasonable
thing to do to a real, shared, third-party service for a demo. The 403
response built below reproduces GitHub's real, documented shape exactly
(headers and message text both copied from GitHub's own REST API docs on
rate limiting), fed through the *same* connector code that would handle a
real one -- connector.py never knows the difference between a real socket
and this mock, so the code path being exercised is the real one.

Run it directly: `py rate_limit_drill.py`
"""

import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, ".")
import connector_before  # noqa: E402
import connector  # noqa: E402


class _FakeErrorBody:
    """Minimal stand-in for the file object HTTPError wraps."""

    def read(self):
        return (
            b'{"message": "API rate limit exceeded for 203.0.113.1. '
            b"(But here's the good news: Authenticated requests get a "
            b"higher rate limit. Check out the documentation for more "
            b'details.)", "documentation_url": '
            b'"https://docs.github.com/rest/overview/'
            b'resources-in-the-rest-api#rate-limiting"}'
        )

    def close(self):
        pass


class _FakeOkResponse:
    """Minimal stand-in for a successful urlopen() context manager."""

    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


def make_rate_limited_urlopen(reset_in_seconds: int):
    """A fake urlopen that always raises GitHub's real 403 rate-limit
    shape, with a reset time `reset_in_seconds` in the future."""
    reset_at = int(time.time()) + reset_in_seconds

    def _urlopen(req, timeout=10):
        headers = {
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_at),
        }
        raise urllib.error.HTTPError(
            req.full_url, 403, "rate limit exceeded", headers, _FakeErrorBody()
        )

    return _urlopen


def make_ok_urlopen(body: bytes):
    """A fake urlopen that always succeeds, standing in for 'the real
    rate-limit window has now passed'."""
    return lambda req, timeout=10: _FakeOkResponse(body)


if __name__ == "__main__":
    print("--- before: raw error, exactly as an agent would read it ---")
    real_urlopen = urllib.request.urlopen
    urllib.request.urlopen = make_rate_limited_urlopen(reset_in_seconds=3)
    try:
        connector_before.get_file("asadullah48", "crash-course", "README.md")
    except Exception as e:
        print("str(e):", str(e))
    finally:
        urllib.request.urlopen = real_urlopen

    print()
    print("--- after: AX-rewritten message, then a real wait-and-retry ---")
    wait_s = 3
    mock_urlopen = make_rate_limited_urlopen(reset_in_seconds=wait_s)
    try:
        connector.get_file(
            "asadullah48", "crash-course", "README.md", _urlopen=mock_urlopen
        )
    except connector.ConnectorError as e:
        print("ConnectorError:", str(e))

    print(f"(sleeping {wait_s + 1}s, exactly as the message said, for real)")
    time.sleep(wait_s + 1)

    ok_urlopen = make_ok_urlopen(b"# Crash Course Projects\n")
    content = connector.get_file(
        "asadullah48", "crash-course", "README.md", _urlopen=ok_urlopen
    )
    print("SUCCESS after waiting out the window:", content.splitlines()[0])
