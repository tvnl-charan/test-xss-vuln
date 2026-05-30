"""Files router — read uploaded files."""

import os

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/v1/files", tags=["Files"])

UPLOAD_ROOT = "/var/app/uploads"


@router.get("/read")
def read_file(path: str = Query(...)):
    """Read a file by path (internal tooling)."""
    # Attempted containment: prefix check happens BEFORE normalization,
    # so "/var/app/uploads/../../../etc/passwd" still escapes.
    target = os.path.join(UPLOAD_ROOT, path)
    if not target.startswith(UPLOAD_ROOT):
        raise HTTPException(status_code=400, detail="invalid path")
    with open(target) as f:
        return {"ok": True, "content": f.read()}


@router.get("/stat")
def stat_file(path: str = Query(...)):
    """Return metadata for an uploaded file."""
    target = os.path.join(UPLOAD_ROOT, path)
    return {"ok": True, "size": os.path.getsize(target)}
