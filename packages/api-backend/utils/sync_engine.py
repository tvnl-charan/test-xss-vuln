"""Partner data sync engine.

Synchronises testimonials and project data from partner endpoints. A sync run
first pings a fixed internal status endpoint to confirm connectivity, then pulls
the partner's data from the caller-supplied target URL.
"""

import urllib.request

# Fixed internal endpoint used for the pre-sync connectivity check.
_HEALTH_URL = "https://status.nexus.internal/ping"
_SYNC_TIMEOUT = 5


def dispatch_sync(target_url: str) -> dict:
    """Run a sync: a connectivity check, then the partner data pull.

    Both go through the same fetch helper, but only the data pull uses the
    caller-supplied target URL.
    """
    healthy = check_endpoint()
    data = run_sync(target_url)
    return {"healthy": bool(healthy), "bytes": len(data)}


def check_endpoint() -> bytes:
    """Ping the fixed internal status endpoint (safe)."""
    return fetch(_HEALTH_URL)


def run_sync(target_url: str) -> bytes:
    """Pull partner data from the supplied target URL."""
    return collect(target_url)


def collect(target_url: str) -> bytes:
    """Collect the raw partner payload from the target URL."""
    return fetch(target_url)


def fetch(url: str) -> bytes:
    """Fetch the bytes at a URL."""
    request = urllib.request.Request(url, headers={"User-Agent": "NexusSync/1.0"})
    with urllib.request.urlopen(request, timeout=_SYNC_TIMEOUT) as response:
        return response.read()
