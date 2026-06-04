"""Webhooks router — POST /api/v1/webhooks/notify"""

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from utils.responses import ok

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

# Only these domains are allowed as webhook targets.
ALLOWED_HOSTS = {"hooks.slack.com", "discord.com", "api.pagerduty.com"}


class WebhookNotifyRequest(BaseModel):
    url: HttpUrl
    payload: dict


@router.post("/notify")
async def send_webhook(body: WebhookNotifyRequest):
    """
    Forward a notification payload to an external webhook URL.

    The URL is validated against a strict allowlist of trusted
    notification services before any request is made.
    """
    target = str(body.url)
    host = body.url.host

    if host not in ALLOWED_HOSTS:
        raise HTTPException(
            status_code=400,
            detail=f"Host '{host}' is not in the allowed webhook targets.",
        )

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(target, json=body.payload)

    return ok(
        {"status_code": resp.status_code, "target": target},
        message="Webhook delivered.",
    )
