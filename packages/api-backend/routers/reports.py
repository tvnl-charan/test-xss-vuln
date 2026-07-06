"""Reports router — generate, schedule, download, and archive exports."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

from data.store import PROJECTS, contact_submissions, invoices, testimonials
from services import reporting
from utils.responses import ok

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])

_DATASETS = {
    "projects": lambda: PROJECTS,
    "testimonials": lambda: testimonials,
    "contacts": lambda: contact_submissions,
    "invoices": lambda: invoices,
}


class GenerateRequest(BaseModel):
    name: str
    dataset: str


class ScheduleRequest(BaseModel):
    name: str
    dataset: str
    cron: str = "0 0 * * *"


class ArchiveRequest(BaseModel):
    label: str
    report_keys: list[str]


def _dataset_records(dataset: str) -> list[dict]:
    """Resolve a dataset name to its current records."""
    loader = _DATASETS.get(dataset)
    if not loader:
        raise HTTPException(status_code=400, detail="Unknown dataset.")
    return loader()


@router.post("/generate", status_code=201)
def generate_report(payload: GenerateRequest):
    """Generate and persist a CSV report for a dataset."""
    records = _dataset_records(payload.dataset)
    key = reporting.write_report(payload.name, payload.dataset, records)
    return ok({"key": key}, message="Report generated.")


@router.get("/download")
def download_report(name: str = Query(..., description="Name the report was generated under")):
    """Download a previously generated report by name."""
    try:
        data = reporting.read_report(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report not found.")
    return Response(content=data, media_type="text/csv")


@router.post("/schedule", status_code=201)
def schedule_report(payload: ScheduleRequest):
    """Schedule recurring generation of a report."""
    _dataset_records(payload.dataset)  # validate dataset early
    job = reporting.schedule_report(payload.name, payload.dataset, payload.cron)
    return ok(job, message="Report scheduled.")


@router.post("/archive")
def archive_reports(payload: ArchiveRequest):
    """Bundle a set of generated reports into a downloadable archive."""
    path = reporting.archive_reports(payload.label, payload.report_keys)
    return ok({"archive": path}, message="Archive created.")


@router.get("/preview")
def preview_csv(dataset: str = Query("projects")):
    """Return a CSV preview of a dataset inline."""
    records = _dataset_records(dataset)
    return Response(content=reporting.render_csv(dataset, records), media_type="text/csv")
