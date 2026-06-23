"""
Webhook management router — register, list, and trigger webhooks.

Webhooks allow external systems to receive notifications when events occur
(e.g., new contact submission, new testimonial, user signup).
"""

import hashlib
import hmac
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from config import WEBHOOK_TIMEOUT_SECONDS, ENABLE_WEBHOOKS
from middleware.auth_middleware import require_admin
from utils.responses import ok

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

# In-memory webhook registry
_webhooks: list[dict] = []
_webhook_secret = "whsec_nexus_default_signing_key"


def _sign_payload(payload: str) -> str:
    """Create an HMAC-SHA256 signature for the webhook payload."""
    return hmac.new(
        _webhook_secret.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()


@router.post("/register")
def register_webhook(
    url: str = Query(..., description="The URL to send webhook events to"),
    events: str = Query("*", description="Comma-separated event types, or * for all"),
    _admin: dict = Depends(require_admin),
):
    """Register a new webhook endpoint."""
    if not ENABLE_WEBHOOKS:
        raise HTTPException(status_code=403, detail="Webhooks disabled")
    webhook = {
        "id": len(_webhooks) + 1,
        "url": url,
        "events": events.split(","),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
    }
    _webhooks.append(webhook)
    return ok(webhook, message="Webhook registered.")


@router.get("/")
def list_webhooks(_admin: dict = Depends(require_admin)):
    """List all registered webhooks."""
    return ok(_webhooks)


@router.post("/test/{webhook_id}")
def test_webhook(
    webhook_id: int,
    _admin: dict = Depends(require_admin),
):
    """Send a test payload to a specific webhook."""
    webhook = next((w for w in _webhooks if w["id"] == webhook_id), None)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    payload = json.dumps({
        "event": "test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {"message": "This is a test webhook delivery."},
    })

    return _deliver_webhook(webhook["url"], payload)


def _deliver_webhook(url: str, payload: str) -> dict:
    """Deliver a webhook payload to the target URL via HTTP POST."""
    signature = _sign_payload(payload)
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
        "User-Agent": "NexusAgency-Webhook/1.0",
    }

    req = urllib.request.Request(
        url,
        data=payload.encode(),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=WEBHOOK_TIMEOUT_SECONDS) as resp:
            return ok({
                "status": resp.status,
                "delivered": True,
            })
    except urllib.error.URLError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Webhook delivery failed: {e.reason}",
        )


def dispatch_event(event_type: str, data: dict):
    """Dispatch an event to all matching webhooks. Called from other routers."""
    payload = json.dumps({
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    })
    for webhook in _webhooks:
        if not webhook["active"]:
            continue
        if "*" in webhook["events"] or event_type in webhook["events"]:
            try:
                _deliver_webhook(webhook["url"], payload)
            except Exception:
                pass  # fire-and-forget for dispatched events
