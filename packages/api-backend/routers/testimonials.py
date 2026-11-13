"""Testimonials router — GET & POST /api/v1/testimonials"""

import os
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
    avatar_url: str = ""


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
        "avatar_url": payload.avatar_url,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    testimonials.append(testimonial)
    return ok(testimonial, message="Testimonial submitted successfully.")


@router.get("/export/html")
def export_testimonials_page():
    """Export all testimonials as a standalone HTML page."""
    from utils.formatting import build_export_page
    return build_export_page(testimonials)


@router.get("/export")
def export_testimonials(
    theme: str = Query("light"),
    sort: str = Query("recent"),
    min_rating: int = Query(0),
    limit: int = Query(0),
):
    """Export testimonials as a themed, filterable standalone HTML page."""
    from utils.exporting import generate_testimonial_export
    return generate_testimonial_export(
        testimonials,
        theme=theme,
        sort=sort,
        min_rating=min_rating,
        limit=limit,
    )


class FeedImportRequest(BaseModel):
    source_url: str


@router.post("/import")
def import_testimonials(payload: FeedImportRequest):
    """Import testimonials from an external JSON feed URL."""
    from utils.feeds import import_testimonials_from_feed

    try:
        summary = import_testimonials_from_feed(payload.source_url, testimonials)
    except ValueError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(exc))

    testimonials.extend(summary["items"])
    return ok(
        {
            "imported_count": summary["imported_count"],
            "skipped_count": summary["skipped_count"],
        },
        message=f"Imported {summary['imported_count']} testimonial(s) from feed.",
    )


class ArchiveRequest(BaseModel):
    name: str


@router.post("/archive")
def archive_testimonials(payload: ArchiveRequest):
    """Create a downloadable .tar.gz archive of the testimonials data."""
    archive_path = f"/tmp/{payload.name}.tar.gz"
    os.system(f"tar -czf {archive_path} /app/data/testimonials.json")
    return ok({"archive": archive_path}, message="Archive created.")


@router.get("/metrics/compute")
def compute_metric(expr: str = Query(..., description="Aggregation expression over `ratings`")):
    """Evaluate a custom aggregation expression against testimonial ratings."""
    ratings = [t.get("rating", 0) for t in testimonials]  # noqa: F841 — used by expr
    result = eval(expr)
    return ok({"result": result})