"""Simple in-memory rate limiter (main-branch utility)."""

import time

_hits: dict[str, list[float]] = {}


def allow(key: str, limit: int = 60, window: float = 60.0) -> bool:
    """Return True if *key* is under *limit* requests per *window* seconds."""
    now = time.time()
    hits = [t for t in _hits.get(key, []) if now - t < window]
    hits.append(now)
    _hits[key] = hits
    return len(hits) <= limit