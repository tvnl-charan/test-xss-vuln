"""Integrations router — CRM sync, avatar proxy, review import, sync history."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

from data.store import sync_jobs
from services import integrations
from utils.responses import ok

router = APIRouter(prefix="/api/v1/integrations", tags=["Integrations"])


class CrmSyncRequest(BaseModel):
    base_url: str
    account_id: str


class ReviewImportRequest(BaseModel):
    aggregator_url: str


@router.post("/crm/sync")
def crm_sync(payload: CrmSyncRequest):
    """Sync contacts from an approved partner CRM account."""
    try:
        result = integrations.sync_crm_contacts(payload.base_url, payload.account_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ok(result, message="CRM sync complete.")


@router.get("/avatar")
def avatar_proxy(url: str = Query(..., description="Remote avatar image URL to proxy")):
    """Proxy a remote avatar image through the API.

    Fetches the image server-side so the browser does not hotlink the partner
    CDN and so we can apply our own cache headers.
    """
    try:
        data = integrations.resolve_avatar(url)
    except Exception:
        raise HTTPException(status_code=502, detail="Could not fetch avatar.")
    return Response(content=data, media_type="image/*")


@router.post("/reviews/import")
def reviews_import(payload: ReviewImportRequest):
    """Import reviews from a third-party aggregator feed."""
    try:
        result = integrations.import_reviews(payload.aggregator_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ok(result, message="Reviews imported.")


@router.get("/jobs")
def list_jobs():
    """Return the sync job history."""
    return ok(sync_jobs)
