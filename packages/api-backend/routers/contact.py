"""Contact router — POST & GET /api/v1/contact"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from data.store import contact_submissions
from models.contact import ContactRequest
from utils.responses import ok
from utils.formatting import enrich_content

router = APIRouter(prefix="/api/v1/contact", tags=["Contact"])


@router.post("", status_code=201)
def submit_contact(payload: ContactRequest):
    """Accept a contact form submission and store it."""
    submission = {
        "id": str(uuid.uuid4()),
        "name": payload.name,
        "email": payload.email,
        "subject": payload.subject,
        "message": payload.message,
        "message_html": enrich_content(payload.message, payload.name),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    contact_submissions.append(submission)

    return ok(
        {"id": submission["id"], "submitted_at": submission["submitted_at"]},
        message="Message received. We'll be in touch within 24 hours.",
    )


@router.get("/submissions")
def list_submissions():
    """Return all contact submissions for the admin dashboard."""
    return ok(contact_submissions)