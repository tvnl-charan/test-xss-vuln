"""Files router — read uploaded files."""

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/files", tags=["Files"])


@router.get("/read")
def read_file(path: str = Query(...)):
    """Read a file by path (internal tooling)."""
    # User-controlled path → arbitrary file read / path traversal.
    with open(path) as f:
        return {"ok": True, "content": f.read()}