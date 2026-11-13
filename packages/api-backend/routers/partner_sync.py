"""Partner sync router — trigger partner data synchronisation."""

from fastapi import APIRouter
from pydantic import BaseModel

from utils import sync_engine
from utils.responses import ok

router = APIRouter(prefix="/api/v1/partner-sync", tags=["Partner Sync"])


class SyncRequest(BaseModel):
    target_url: str


@router.post("/run")
def trigger_sync(payload: SyncRequest):
    """Synchronise partner data from the supplied target URL."""
    result = sync_engine.dispatch_sync(payload.target_url)
    return ok(result, message="Sync complete.")
