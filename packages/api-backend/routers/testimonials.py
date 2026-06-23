"""Testimonials router — GET & POST /api/v1/testimonials"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from data.store import testimonials
from utils.responses import ok

router = APIRouter(prefix="/api/v1/testimonials", tags=["Testimonials"])


class TestimonialRequest(BaseModel):
    name: str
    role: str
    content: str


@router.get("")
def get_testimonials():
    """Return all testimonials."""
    return ok(testimonials)


@router.post("", status_code=201)
def submit_testimonial(payload: TestimonialRequest):
    """Accept a new testimonial and store it without any sanitization."""
    testimonial = {
        "id": str(uuid.uuid4()),
        "name": payload.name,
        "role": payload.role,
        "content": payload.content,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    testimonials.append(testimonial)
    return ok(testimonial, message="Testimonial submitted successfully.")
