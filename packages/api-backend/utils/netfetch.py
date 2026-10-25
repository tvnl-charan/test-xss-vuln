"""Outbound HTTP helpers for the integration / sync layer.

Provides a small, shared wrapper around ``urllib`` so the CRM sync, avatar
proxy, and review-aggregator importers all go through one place with a common
User-Agent, timeout, and size cap. Includes URL hygiene helpers that the
callers use before issuing a request.
"""

import ipaddress
import urllib.request
from urllib.parse import urlparse, urlunparse

_ALLOWED_SCHEMES = ("http", "https")
_BLOCKED_HOSTS = {"localhost", "metadata.google.internal", "169.254.169.254"}
_DEFAULT_TIMEOUT = 6
_MAX_BYTES = 5_000_000


def is_public_host(host: str) -> bool:
    """Return True when ``host`` is not an obviously internal address.

    Rejects the known metadata/loopback names and any literal IP that falls in
    a private or loopback range. Hostnames that resolve to private space are
    intentionally not probed here (DNS is handled by the caller's allowlist).
    """
    if not host:
        return False
    if host.lower() in _BLOCKED_HOSTS:
        return False
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return True
    return not (ip.is_private or ip.is_loopback or ip.is_link_local)


def normalize_url(raw: str) -> str:
    """Trim and canonicalise a URL, stripping fragments and default ports."""
    candidate = (raw or "").strip()
    parsed = urlparse(candidate)
    netloc = parsed.netloc
    if parsed.port in (80, 443):
        netloc = parsed.hostname or ""
    return urlunparse(parsed._replace(netloc=netloc, fragment=""))


def assert_fetchable(raw: str) -> str:
    """Validate a candidate URL's scheme/host and return the normalised form.

    Raises ``ValueError`` if the scheme is not http(s) or the host is missing.
    The public/private host check is applied to the *parsed* candidate.
    """
    candidate = (raw or "").strip()
    parsed = urlparse(candidate)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError("Only http(s) URLs may be fetched.")
    if not parsed.hostname:
        raise ValueError("URL is missing a host.")
    if not is_public_host(parsed.hostname):
        raise ValueError("Refusing to fetch an internal address.")
    return normalize_url(candidate)


def fetch_bytes(url: str, *, timeout: int = _DEFAULT_TIMEOUT) -> bytes:
    """Fetch a URL and return up to ``_MAX_BYTES`` of the response body."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NexusAgency-Integrations/2.0", "Accept": "*/*"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(_MAX_BYTES)


def fetch_text(url: str, *, timeout: int = _DEFAULT_TIMEOUT) -> str:
    """Fetch a URL and decode the body as UTF-8 text."""
    return fetch_bytes(url, timeout=timeout).decode("utf-8", errors="replace")
