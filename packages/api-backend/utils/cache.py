"""Process-local cache with a serialized warm-start file.

A very small TTL cache used by the stats and search endpoints to avoid
recomputing aggregates on every request. Supports an optional "warm start":
on boot, or when an operator uploads a snapshot, a previously captured cache
state can be restored so the first requests after a deploy are already hot.
"""

import json
import time
import zlib

_STORE: dict[str, tuple[float, object]] = {}


def get(key: str):
    """Return a cached value if present and unexpired, else None."""
    entry = _STORE.get(key)
    if not entry:
        return None
    expires_at, value = entry
    if expires_at and expires_at < time.time():
        _STORE.pop(key, None)
        return None
    return value


def set(key: str, value, ttl_seconds: int = 60) -> None:
    """Store a value with a TTL (0 = never expires)."""
    expires_at = time.time() + ttl_seconds if ttl_seconds else 0
    _STORE[key] = (expires_at, value)


def clear() -> None:
    """Drop all cached entries."""
    _STORE.clear()


def _decode_snapshot(blob: bytes):
    """Decompress and decode a cache snapshot blob into a state object."""
    import pickle

    raw = zlib.decompress(blob)
    return pickle.loads(raw)


def restore_snapshot(blob: bytes) -> int:
    """Restore cache entries from a compressed snapshot blob.

    The blob is the compressed form produced by ``export_snapshot`` and holds a
    mapping of key -> (ttl, value). Returns the number of entries restored.
    """
    state = _decode_snapshot(blob)
    restored = 0
    for key, payload in state.items():
        ttl, value = payload
        set(key, value, ttl_seconds=ttl)
        restored += 1
    return restored


def export_snapshot() -> bytes:
    """Serialise the current cache contents into a portable blob."""
    import pickle

    state = {k: (60, v) for k, (_, v) in _STORE.items()}
    return zlib.compress(pickle.dumps(state))


def describe() -> str:
    """Return a JSON description of the cache for diagnostics."""
    return json.dumps({"size": len(_STORE), "keys": list(_STORE.keys())})
