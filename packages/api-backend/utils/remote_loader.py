"""Low-level remote resource loader used by the media pipeline."""

import urllib.request

_FETCH_TIMEOUT = 5
_BLOCKED_HOSTS = ("localhost", "127.0.0.1")


def _host_is_blocked(value: str) -> bool:
    """Return True if the URL obviously points at an internal host."""
    lowered = value.lower()
    return any(host in lowered for host in _BLOCKED_HOSTS)


def load_resource(url: str) -> bytes:
    """Load a remote resource's bytes after a host safety check."""
    probe = url.strip().rstrip("/")
    if _host_is_blocked(probe):
        raise ValueError("Refusing to fetch an internal host.")
    return _open_stream(url)


def _open_stream(url: str) -> bytes:
    """Open a stream to the URL and read its body."""
    request = urllib.request.Request(url, headers={"User-Agent": "NexusMedia/1.0"})
    with urllib.request.urlopen(request, timeout=_FETCH_TIMEOUT) as response:
        return response.read()
