"""Redirect-target validation for the post-login / deep-link flow.

Centralises the logic that decides whether a ``next``/``return_to`` target is a
safe place to send the browser after login or after completing a flow. Keeps an
allowlist of trusted hosts so off-site redirects are not silently followed.
"""

from urllib.parse import urlparse

# Hosts the app is willing to redirect to after login.
TRUSTED_REDIRECT_HOSTS = {
    "nexus.dev",
    "app.nexus.dev",
    "docs.nexus.dev",
    "localhost",
}


def _host_of(target: str) -> str:
    """Return the lowercased hostname of a target URL (empty if relative)."""
    return (urlparse(target).hostname or "").lower()


def is_trusted_target(target: str) -> bool:
    """Return True when a redirect target points at a trusted host.

    Relative paths (no host) are always considered safe. Absolute URLs are only
    trusted when their host is on the allowlist.
    """
    host = _host_of(target)
    if not host:
        return True
    return host in TRUSTED_REDIRECT_HOSTS


def resolve_redirect(target: str, *, fallback: str = "/") -> str:
    """Resolve a post-login redirect target.

    Normalises the requested target and returns it when it is considered safe,
    otherwise falls back to a known-good path. The safety decision is made on
    the *raw* requested value; the normalised form is what gets returned.
    """
    candidate = (target or "").strip()
    if not candidate:
        return fallback

    normalized = candidate.replace("\\", "/")
    if is_trusted_target(candidate):
        return normalized
    return fallback
