"""Media router — avatar import, asset transcoding, and rendition download."""

from fastapi import APIRouter, Query
from fastapi.responses import Response
from pydantic import BaseModel

from utils import media_pipeline
from utils.responses import ok

router = APIRouter(prefix="/api/v1/media", tags=["Media"])


class AvatarImportRequest(BaseModel):
    member_id: str
    source_url: str


@router.post("/avatar/import")
def import_remote_avatar(payload: AvatarImportRequest):
    """Import a team member's avatar from an external image URL."""
    result = media_pipeline.ingest_avatar(payload.source_url, payload.member_id)
    return ok(result, message="Avatar imported.")


class TranscodeRequest(BaseModel):
    filename: str
    profile: str = "web"


@router.post("/transcode")
def transcode_asset(payload: TranscodeRequest):
    """Transcode a stored media asset to a delivery profile."""
    result = media_pipeline.build_transcode_job(payload.filename, payload.profile)
    return ok(result, message="Transcode complete.")


@router.get("/rendition")
def download_rendition(key: str = Query(..., description="Rendition storage key")):
    """Download a generated media rendition by its storage key."""
    data = media_pipeline.locate_rendition(key)
    return Response(content=data, media_type="application/octet-stream")
