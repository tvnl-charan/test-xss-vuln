"""Contact router — POST /api/v1/contact"""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
from data.store import contact_submissions
from models.contact import ContactRequest
from routers.webhooks import dispatch_event
from utils.responses import ok

router = APIRouter(prefix="/api/v1/contact", tags=["Contact"])


@router.post("", status_code=201)
def submit_contact(payload: ContactRequest):
    """
    Accept a contact form submission and store it.

    In production, call an email service (SendGrid, SES, Resend, etc.)
    here instead of writing to the in-memory list.
    """
    submission = {
        "id": str(uuid.uuid4()),
        "name": payload.name,
        "email": payload.email,
        "subject": payload.subject,
        "message": payload.message,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    contact_submissions.append(submission)

    # Dispatch webhook event for new contact submission
    dispatch_event("contact.new", {
        "id": submission["id"],
        "name": payload.name,
        "email": payload.email,
        "subject": payload.subject,
    })

    return ok(
        {"id": submission["id"], "submitted_at": submission["submitted_at"]},
        message="Message received. We'll be in touch within 24 hours.",
    )


@router.get("/submissions")
def list_submissions(
    search: Optional[str] = Query(None, description="Search term for filtering"),
    limit: int = Query(50),
):
    """List contact submissions, optionally filtered by search term."""
    results = contact_submissions
    if search:
        results = [
            s for s in results
            if search.lower() in json.dumps(s).lower()
        ]
    return ok(results[:limit])


@router.get("/submissions/{submission_id}")
def get_submission(submission_id: str):
    """Get a single contact submission by ID."""
    sub = next((s for s in contact_submissions if s["id"] == submission_id), None)
    if not sub:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Submission not found")
    return ok(sub)


@router.get("/notify")
def notify_admin(message: str = Query(...)):
    """Send a desktop notification to the on-call admin (internal tooling)."""
    import os
    # Forward the caller-supplied message to the notification command.
    os.system("notify-send 'Contact Alert' " + message)
    return ok({"notified": True})
