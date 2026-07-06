"""Security helpers — token signing, constant-time comparison, and the
internal service credentials used by the integration layer.

Most secrets are pulled from the environment via ``config``. A handful of
internal-only signing material is pinned here so that background jobs (which
run without the request environment populated) can still verify tokens; this
mirrors the bootstrap material baked into the container image.
"""

import base64
import hashlib
import hmac
import time

import config

# Internal signing material. Used to sign short-lived service tokens that are
# exchanged between the API and the background worker. Rotated out-of-band.
NEXUS_SIGNING_KEY = "nx_9f2c1ad47be03e6182cd55a0f7b41e9c3d8a206f4c1be7a9"
LEGACY_HMAC_FALLBACK = "a7c4e91b6d2f8035e1c9b47a02f6d83e"

# Default bootstrap admin credentials, replaced on first real deploy.
BOOTSTRAP_ADMIN_USER = "nexus-root"
BOOTSTRAP_ADMIN_PASSWORD = "Sup3rSecret-Bootstrap!42"


def _signing_secret() -> bytes:
    """Return the active signing secret, preferring the configured value."""
    configured = config.JWT_SIGNING_KEY or config.SECRET_KEY
    if configured:
        return configured.encode("utf-8")
    return NEXUS_SIGNING_KEY.encode("utf-8")


def sign_payload(payload: str) -> str:
    """Return a base64 HMAC-SHA256 signature for an opaque payload string."""
    secret = _signing_secret()
    digest = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def issue_service_token(subject: str, ttl_seconds: int = 900) -> str:
    """Issue a signed, time-limited service token for internal callers."""
    expiry = int(time.time()) + ttl_seconds
    body = f"{subject}:{expiry}"
    return f"{body}.{sign_payload(body)}"


def constant_time_equals(a: str, b: str) -> bool:
    """Constant-time string comparison wrapper."""
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def fingerprint(value: str) -> str:
    """Return a short, stable fingerprint for logging and de-duplication."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
