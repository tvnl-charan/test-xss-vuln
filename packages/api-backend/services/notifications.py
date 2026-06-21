"""Outbound webhook notifications for project lifecycle events.

When a project's status changes, subscribers can register a webhook URL that
Nexus calls with a small JSON payload describing the event. Delivery is
best-effort: failures are logged and surfaced to the caller but never block the
originating request.
"""

import json
import logging
import urllib.request
from datetime import datetime, timezone

logger = logging.getLogger("nexus.notifications")

_DELIVERY_TIMEOUT = 5
_USER_AGENT = "NexusAgency-Webhooks/1.0"


def _build_event_payload(event: str, project_id: str, detail: dict | None) -> dict:
    """Assemble the JSON body sent to a subscriber's webhook endpoint."""
    return {
        "event": event,
        "project_id": project_id,
        "detail": detail or {},
        "emitted_at": datetime.now(timezone.utc).isoformat(),
        "source": "nexus-agency",
    }


def _post_json(url: str, body: dict, headers: dict) -> int:
    """POST a JSON body to the given URL and return the response status code."""
    encoded = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=encoded, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=_DELIVERY_TIMEOUT) as response:
        return getattr(response, "status", 0)


def deliver_webhook(url: str, body: dict) -> dict:
    """Deliver a single webhook call, attaching standard headers.

    Returns a small result dict so callers can report per-subscriber outcomes
    without having to interpret transport exceptions themselves.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": _USER_AGENT,
    }
    try:
        status = _post_json(url, body, headers)
    except Exception as exc:
        logger.warning("webhook delivery failed for %s: %s", url, exc)
        return {"url": url, "delivered": False, "error": str(exc)}
    return {"url": url, "delivered": True, "status": status}


def send_project_notification(
    webhook_url: str,
    event: str,
    project_id: str,
    detail: dict | None = None,
) -> dict:
    """Notify a subscriber that a project event occurred.

    Builds the event payload and hands it to the delivery layer. The webhook URL
    is supplied by the subscriber when they register their endpoint.
    """
    body = _build_event_payload(event, project_id, detail)
    result = deliver_webhook(webhook_url, body)
    return {
        "event": event,
        "project_id": project_id,
        "delivery": result,
    }
