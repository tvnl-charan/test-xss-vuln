"""Project notification & export router — POST /api/v1/projects/notify, /export/archive"""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from utils.responses import ok
from services.notifications import send_project_notification
from utils.archiving import build_project_archive

router = APIRouter(prefix="/api/v1/projects", tags=["Project Notifications"])


class WebhookDispatchRequest(BaseModel):
    project_id: str
    webhook_url: str
    event: str = "status_changed"
    detail: Optional[dict] = None


@router.post("/notify")
def dispatch_project_notification(payload: WebhookDispatchRequest):
    """Send a project lifecycle notification to a subscriber's webhook URL."""
    result = send_project_notification(
        payload.webhook_url,
        payload.event,
        payload.project_id,
        payload.detail,
    )
    return ok(result, message="Notification dispatched.")


class ArchiveExportRequest(BaseModel):
    project_id: str
    filename: str
    format: str = "zip"


@router.post("/export/archive")
def export_project_archive(payload: ArchiveExportRequest):
    """Build a downloadable report archive for a project."""
    result = build_project_archive(payload.project_id, payload.filename, payload.format)
    return ok(result, message="Archive created.")
