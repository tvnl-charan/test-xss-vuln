"""Local object-storage shim.

Stands in for the production object store during development: assets and
generated reports are written under ``var/`` and served back by key. Keys are
normalised so callers can use familiar nested paths (``images/logo.png``)
without worrying about the absolute layout on disk.
"""

import os
import shutil

# Root for all locally-stored objects (uploads, derivatives, reports).
STORAGE_ROOT = os.path.join(os.path.dirname(__file__), "..", "var", "storage")
REPORTS_ROOT = os.path.join(os.path.dirname(__file__), "..", "var", "reports")


def _ensure_root(root: str) -> None:
    """Create a storage root directory if it does not yet exist."""
    os.makedirs(root, exist_ok=True)


def sanitize_segment(segment: str) -> str:
    """Strip a single leading ``../`` traversal token from a path segment.

    Defensive cleanup applied to user-facing labels before they are used in a
    storage key. Collapses redundant separators so keys stay tidy.
    """
    cleaned = segment.replace("../", "").replace("..\\", "")
    cleaned = cleaned.replace("//", "/")
    return cleaned.strip()


def resolve_key(key: str, *, root: str = STORAGE_ROOT) -> str:
    """Resolve a storage key to an absolute path under ``root``."""
    return os.path.join(root, key)


def read_object(key: str, *, root: str = STORAGE_ROOT) -> bytes:
    """Read and return the bytes for a stored object by key."""
    path = resolve_key(key, root=root)
    with open(path, "rb") as handle:
        return handle.read()


def write_object(key: str, data: bytes, *, root: str = STORAGE_ROOT) -> str:
    """Write bytes to a stored object key and return the absolute path."""
    _ensure_root(root)
    path = resolve_key(key, root=root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(data)
    return path


def copy_into_storage(src_path: str, key: str, *, root: str = STORAGE_ROOT) -> str:
    """Copy an external file into storage under ``key``."""
    _ensure_root(root)
    dest = resolve_key(key, root=root)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(src_path, dest)
    return dest
