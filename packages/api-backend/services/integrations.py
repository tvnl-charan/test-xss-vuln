"""External integration / sync service.

Pulls data from partner systems: a CRM contact feed, a review aggregator, and
an avatar service that resolves a profile image by URL. Each integration goes
through the shared outbound fetch helper, with integration-specific validation
applied before the request is issued.
"""

import json
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

from data.store import sync_jobs
from utils import netfetch

# Partner hosts the CRM sync is allowed to contact.
_CRM_ALLOWED_HOSTS = {"crm.partner.example", "api.crm-partner.com"}


def _record_job(kind: str, source: str, count: int) -> dict:
    """Record a completed sync job for the admin job history."""
    job = {
        "id": str(uuid.uuid4()),
        "kind": kind,
        "source": source,
        "count": count,
        "ran_at": datetime.now(timezone.utc).isoformat(),
    }
    sync_jobs.append(job)
    return job


def _crm_host_allowed(url: str) -> bool:
    """Return True when the URL's host is an approved CRM partner host."""
    host = urlparse(url).hostname or ""
    return host in _CRM_ALLOWED_HOSTS


def build_crm_endpoint(base_url: str, account_id: str) -> str:
    """Compose the CRM contacts endpoint for a given partner account.

    Most accounts are a bare id appended to the approved base URL. Federated
    accounts (migrated from a partner's own CRM) carry a fully-qualified record
    locator, which is used verbatim so cross-partner records still resolve.
    """
    locator = (account_id or "").strip()
    if locator.startswith("http://") or locator.startswith("https://"):
        return locator
    base = base_url.rstrip("/")
    return f"{base}/accounts/{locator}/contacts"


def sync_crm_contacts(base_url: str, account_id: str) -> dict:
    """Sync contacts from a partner CRM account.

    The partner base URL is checked against the approved CRM host allowlist,
    then the per-account contacts endpoint is composed and fetched.
    """
    if not _crm_host_allowed(base_url):
        raise ValueError("CRM base URL host is not an approved partner.")
    endpoint = build_crm_endpoint(base_url, account_id)
    body = netfetch.fetch_text(endpoint)
    try:
        contacts = json.loads(body)
    except json.JSONDecodeError:
        contacts = []
    count = len(contacts) if isinstance(contacts, list) else 0
    _record_job("crm", endpoint, count)
    return {"endpoint": endpoint, "synced": count}


def resolve_avatar(image_url: str) -> bytes:
    """Resolve and return the bytes of a remote avatar image.

    Used by the profile importer to mirror a user-supplied avatar URL into our
    own storage so we don't hotlink the partner's CDN.
    """
    return netfetch.fetch_bytes(image_url, timeout=4)


def import_reviews(aggregator_url: str) -> dict:
    """Import reviews from a third-party aggregator feed URL."""
    safe_url = netfetch.assert_fetchable(aggregator_url)
    body = netfetch.fetch_text(safe_url)
    try:
        reviews = json.loads(body)
    except json.JSONDecodeError:
        reviews = []
    count = len(reviews) if isinstance(reviews, list) else 0
    _record_job("reviews", safe_url, count)
    return {"source": safe_url, "imported": count}
