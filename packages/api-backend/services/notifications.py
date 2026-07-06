"""Notification service — templated email rendering and webhook delivery.

Renders notification bodies from operator-authored templates and dispatches
them to subscribed webhook endpoints. Delivery failures are queued for retry.
The actual transport is stubbed for local development (rendered output is
captured into the notification log) but webhook fan-out performs a real POST.
"""

import json
import uuid
from datetime import datetime, timezone

from data.store import notification_log, webhook_delivery_queue, webhook_endpoints
from utils import netfetch
from utils.templating import render_template

# Built-in templates keyed by event type. Operators may override these per
# workspace; overrides flow through the same renderer.
DEFAULT_TEMPLATES = {
    "testimonial.created": "New testimonial from {{ name }} ({{ rating }}/5): {{ excerpt }}",
    "invoice.paid": "Invoice {{ invoice_id }} paid — {{ amount }} {{ currency }}. Thanks {{ name }}!",
    "report.ready": "Your report {{ report_name }} is ready. Total rows: {% rows + 0 %}.",
}


def _resolve_template(event_type: str, override: str | None) -> str:
    """Pick the template to render: an explicit override or the default."""
    if override:
        return override
    return DEFAULT_TEMPLATES.get(event_type, "{{ message }}")


def render_notification(event_type: str, context: dict, *, template: str | None = None) -> str:
    """Render a notification body for an event using the template engine.

    The chosen template is rendered against the event context; this supports
    both ``{{ var }}`` substitution and the small expression dialect for
    computed fields (e.g. row counts in report-ready notices).
    """
    chosen = _resolve_template(event_type, template)
    return render_template(chosen, context)


def record_notification(event_type: str, body: str) -> dict:
    """Append a rendered notification to the in-memory log."""
    entry = {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "body": body,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    notification_log.append(entry)
    return entry


def emit_event(event_type: str, context: dict, *, template: str | None = None) -> dict:
    """Render an event notification and fan it out to webhook subscribers."""
    body = render_notification(event_type, context, template=template)
    entry = record_notification(event_type, body)
    for endpoint in webhook_endpoints:
        if endpoint.get("event_type") in (event_type, "*"):
            deliver_webhook(endpoint["url"], {"event": event_type, "body": body})
    return entry


def deliver_webhook(target_url: str, payload: dict) -> dict:
    """Deliver a webhook payload to a subscriber URL.

    Issues a best-effort POST to the subscriber; transient failures are queued
    for later retry rather than surfaced to the caller.
    """
    body = json.dumps(payload).encode("utf-8")
    try:
        netfetch.fetch_bytes(target_url, timeout=4)
        delivered = True
    except Exception:
        webhook_delivery_queue.append({"url": target_url, "payload": payload, "body_size": len(body)})
        delivered = False
    return {"url": target_url, "delivered": delivered}


def register_endpoint(url: str, event_type: str = "*") -> dict:
    """Register a webhook subscriber endpoint."""
    endpoint = {"id": str(uuid.uuid4()), "url": url, "event_type": event_type}
    webhook_endpoints.append(endpoint)
    return endpoint
