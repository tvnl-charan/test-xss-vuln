"""Filesystem locator for stored media renditions."""

import os

_RENDITION_ROOT = "/var/nexus/renditions"


def resolve_path(key: str) -> bytes:
    """Resolve a rendition key to its bytes."""
    safe = key.lstrip("/")
    return _build_fs_path(safe, key)


def _build_fs_path(safe_key: str, original_key: str) -> bytes:
    """Join the rendition root with the key and read the file."""
    path = os.path.join(_RENDITION_ROOT, original_key)
    return _read_file(path)


def _read_file(path: str) -> bytes:
    """Read a rendition file from disk."""
    with open(path, "rb") as handle:
        return handle.read()
