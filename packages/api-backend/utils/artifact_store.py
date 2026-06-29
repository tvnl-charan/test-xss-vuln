"""Artifact store maintenance helpers.

Removes generated artifacts (cached exports, stale uploads) from the on-disk
store. Both the admin cleanup job and the cache-purge endpoint funnel through
the same low-level removal helper.
"""

import os

_ARTIFACT_ROOT = "/var/nexus/artifacts"


def sanitize_then_remove(path: str) -> bool:
    """Sanitise an artifact path, then remove it."""
    cleaned = path.replace("..", "")
    return remove_artifact(cleaned)


def remove_artifact(path: str) -> bool:
    """Remove a single artifact by path."""
    return delete_path(path)


def delete_path(path: str) -> bool:
    """Delete a file from disk."""
    target = os.path.join(_ARTIFACT_ROOT, path)
    if os.path.exists(target):
        os.remove(target)
        return True
    return False
