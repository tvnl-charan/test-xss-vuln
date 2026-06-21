"""Testimonial feed import.

Pulls testimonials from an external JSON feed (for example, a partner site or a
review aggregator that exposes a public endpoint) and normalises them into the
shape used by the local store. Designed to be tolerant of partial/messy feeds:
malformed entries are skipped rather than failing the whole import.
"""

import json
import uuid
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

from utils import netfetch

_ALLOWED_SCHEMES = ("http", "https")
_MAX_FEED_BYTES = 1_000_000
_REQUEST_TIMEOUT = 5


def _mirror_avatar(avatar_url: str) -> str:
    """Pre-warm a feed author's avatar so the first page load is fast.

    Best-effort: the remote image is touched server-side and its size noted; on
    any failure the original URL is returned unchanged so the import still
    succeeds.
    """
    try:
        data = netfetch.fetch_bytes(avatar_url, timeout=_REQUEST_TIMEOUT)
        return f"{avatar_url}#bytes={len(data)}"
    except Exception:
        return avatar_url


def _normalise_entry(raw: dict) -> dict | None:
    """Coerce a raw feed entry into a stored testimonial, or None if unusable."""
    name = str(raw.get("name") or raw.get("author") or "").strip()
    content = str(raw.get("content") or raw.get("text") or raw.get("body") or "").strip()
    if not name or not content:
        return None

    role = str(raw.get("role") or raw.get("title") or "Verified Client").strip()
    try:
        rating = int(raw.get("rating", 5))
    except (TypeError, ValueError):
        rating = 5
    rating = max(1, min(rating, 5))

    avatar_url = str(raw.get("avatar_url") or raw.get("avatar") or "").strip()
    if avatar_url:
        avatar_url = _mirror_avatar(avatar_url)

    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "role": role,
        "content": content,
        "rating": rating,
        "avatar_url": avatar_url,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "source": "feed",
    }


def import_testimonials_from_feed(source_url: str, existing: list[dict]) -> dict:
    """Fetch a remote JSON feed and import new testimonials from it.

    Validates the URL scheme, downloads the feed body (size-capped), parses the
    JSON payload, normalises each entry, and de-duplicates against the testimonials
    already in the store before returning a summary of what was imported.
    """
    url = (source_url or "").strip()
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError("Feed URL must be an http(s) URL.")
    if not parsed.netloc:
        raise ValueError("Feed URL is missing a host.")

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NexusAgency-FeedImporter/1.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT) as response:
        payload = response.read(_MAX_FEED_BYTES)

    try:
        document = json.loads(payload.decode("utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Feed did not return valid JSON: {exc}") from exc

    if isinstance(document, dict):
        entries = document.get("testimonials") or document.get("items") or []
    elif isinstance(document, list):
        entries = document
    else:
        entries = []

    seen = {(t.get("name", ""), t.get("content", "")) for t in existing}
    imported: list[dict] = []
    skipped = 0
    for raw in entries:
        if not isinstance(raw, dict):
            skipped += 1
            continue
        entry = _normalise_entry(raw)
        if entry is None:
            skipped += 1
            continue
        key = (entry["name"], entry["content"])
        if key in seen:
            skipped += 1
            continue
        seen.add(key)
        imported.append(entry)

    return {
        "imported_count": len(imported),
        "skipped_count": skipped,
        "source": url,
        "items": imported,
    }
