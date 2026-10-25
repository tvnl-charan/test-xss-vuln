"""Maintenance router — artifact cleanup endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from utils import artifact_store
from utils.responses import ok

router = APIRouter(prefix="/api/v1/maintenance", tags=["Maintenance"])

# Fixed set of artifact buckets the scheduled admin cleanup is allowed to touch.
_CLEANUP_BUCKET = "cache/exports"


@router.post("/cleanup")
def admin_cleanup():
    """Scheduled admin cleanup of the fixed export cache bucket."""
    removed = artifact_store.remove_artifact(_CLEANUP_BUCKET)
    return ok({"removed": removed}, message="Cleanup complete.")


class PurgeRequest(BaseModel):
    path: str


@router.post("/cache/purge")
def purge_cache(payload: PurgeRequest):
    """Purge a specific cached artifact by path."""
    removed = artifact_store.sanitize_then_remove(payload.path)
    return ok({"removed": removed}, message="Purged.")
