"""Testimonials router — GET & POST /api/v1/testimonials"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Query
from pydantic import BaseModel

from data.store import testimonials
from utils.responses import ok
from utils.formatting import render_testimonial_html

router = APIRouter(prefix="/api/v1/testimonials", tags=["Testimonials"])


class TestimonialRequest(BaseModel):
    name: str
    role: str
    content: str
    rating: int = 5


@router.get("")
def get_testimonials(format: str = Query("html", enum=["html", "raw"])):
    """Return all testimonials, optionally with HTML-formatted content."""
    if format == "html":
        return ok([render_testimonial_html(t) for t in testimonials])
    return ok(testimonials)


@router.get("/{testimonial_id}")
def get_testimonial(testimonial_id: str):
    """Return a single testimonial by ID."""
    match = next((t for t in testimonials if t["id"] == testimonial_id), None)
    if not match:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Testimonial not found.")
    return ok(render_testimonial_html(match))


@router.post("", status_code=201)
def submit_testimonial(payload: TestimonialRequest):
    """Accept a new testimonial and store it."""
    testimonial = {
        "id": str(uuid.uuid4()),
        "name": payload.name,
        "role": payload.role,
        "content": payload.content,
        "rating": payload.rating,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    testimonials.append(testimonial)
    return ok(testimonial, message="Testimonial submitted successfully.")


@router.get("/export/html")
def export_testimonials_page():
    """Export all testimonials as a standalone HTML page."""
    from utils.formatting import build_export_page
    return build_export_page(testimonials)