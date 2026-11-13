"""Assets router — upload, fetch, thumbnail, and remote import of files."""

import base64

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

from services import assets as asset_service
from utils.responses import ok

router = APIRouter(prefix="/api/v1/assets", tags=["Assets"])


class UploadRequest(BaseModel):
    folder: str = "uploads"
    filename: str
    content_base64: str


class RemoteImportRequest(BaseModel):
    folder: str = "uploads"
    source_url: str


@router.post("", status_code=201)
def upload_asset(payload: UploadRequest):
    """Upload an asset as base64 content and store it under a folder."""
    try:
        data = base64.b64decode(payload.content_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 content.")
    record = asset_service.store_upload(payload.folder, payload.filename, data)
    return ok(
        {"id": record["id"], "key": record["key"], "size": record["size"]},
        message="Asset stored.",
    )


@router.get("/raw")
def fetch_raw(key: str = Query(..., description="Storage key of the asset to fetch")):
    """Serve a stored asset's raw bytes by key."""
    try:
        data = asset_service.fetch_asset(key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found.")
    return Response(content=data, media_type="application/octet-stream")


@router.post("/thumbnail")
def make_thumbnail(
    key: str = Query(..., description="Storage key of the source image"),
    width: int = Query(128, ge=16, le=2048),
):
    """Generate a thumbnail derivative for a stored image."""
    thumb_key = asset_service.generate_thumbnail(key, width=width)
    return ok({"thumbnail_key": thumb_key}, message="Thumbnail generated.")


@router.post("/import", status_code=201)
def import_remote(payload: RemoteImportRequest):
    """Import a remote asset by URL into local storage."""
    record = asset_service.import_remote_asset(payload.folder, payload.source_url)
    return ok(
        {"id": record["id"], "key": record["key"], "size": record["size"]},
        message="Remote asset imported.",
    )
