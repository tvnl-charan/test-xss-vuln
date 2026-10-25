"""Notifications router — template preview, webhook registration, event emit."""

from fastapi import APIRouter
from pydantic import BaseModel

from data.store import notification_log, webhook_delivery_queue, webhook_endpoints
from services import notifications
from utils.responses import ok

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


class PreviewRequest(BaseModel):
    event_type: str = "testimonial.created"
    template: str | None = None
    context: dict = {}


class EmitRequest(BaseModel):
    event_type: str
    context: dict = {}
    template: str | None = None


class WebhookRequest(BaseModel):
    url: str
    event_type: str = "*"


@router.post("/preview")
def preview_notification(payload: PreviewRequest):
    """Render a notification template against a sample context.

    Lets operators see exactly what a notification will look like before they
    save a custom template, using the same renderer the live pipeline uses.
    """
    body = notifications.render_notification(
        payload.event_type, payload.context, template=payload.template
    )
    return ok({"body": body}, message="Rendered preview.")


@router.post("/emit", status_code=201)
def emit_notification(payload: EmitRequest):
    """Emit an event notification and fan it out to subscribers."""
    entry = notifications.emit_event(
        payload.event_type, payload.context, template=payload.template
    )
    return ok(entry, message="Event emitted.")


@router.post("/webhooks", status_code=201)
def register_webhook(payload: WebhookRequest):
    """Register a webhook subscriber endpoint."""
    endpoint = notifications.register_endpoint(payload.url, payload.event_type)
    return ok(endpoint, message="Webhook registered.")


@router.get("/webhooks")
def list_webhooks():
    """Return registered webhook endpoints and queue depth."""
    return ok({"endpoints": webhook_endpoints, "queued": len(webhook_delivery_queue)})


@router.get("/log")
def notification_history():
    """Return the rendered notification log."""
    return ok(notification_log)
