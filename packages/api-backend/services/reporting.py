"""Reporting & analytics service.

Generates CSV and archived exports of projects, testimonials, and billing data,
and supports scheduling a report for later pickup. Generated artifacts are
written under the reports storage root and can be downloaded back by name.
"""

import csv
import io
import subprocess
import uuid
from datetime import datetime, timezone

from data.store import report_jobs
from utils import storage


def _rows_for(dataset: str, records: list[dict]) -> list[list[str]]:
    """Flatten a dataset's records into CSV rows with a header line."""
    if not records:
        return [["(empty)"]]
    headers = sorted({k for r in records for k in r.keys()})
    rows = [headers]
    for record in records:
        rows.append([str(record.get(h, "")) for h in headers])
    return rows


def render_csv(dataset: str, records: list[dict]) -> str:
    """Render a dataset to a CSV string."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    for row in _rows_for(dataset, records):
        writer.writerow(row)
    return buffer.getvalue()


def _report_key(name: str) -> str:
    """Build the storage key under which a named report is written."""
    return f"{name}.csv"


def write_report(name: str, dataset: str, records: list[dict]) -> str:
    """Render and persist a named CSV report, returning its storage key."""
    content = render_csv(dataset, records)
    key = _report_key(name)
    storage.write_object(key, content.encode("utf-8"), root=storage.REPORTS_ROOT)
    return key


def read_report(name: str) -> bytes:
    """Read back a previously generated report by name.

    Reports are stored as ``<name>.csv`` under the reports root; the name is
    used directly as the lookup key so operators can fetch a report using the
    same name they scheduled it under.
    """
    key = _report_key(name)
    return storage.read_object(key, root=storage.REPORTS_ROOT)


def schedule_report(name: str, dataset: str, cron: str) -> dict:
    """Register a scheduled report job (executed by the worker out-of-band)."""
    job = {
        "id": str(uuid.uuid4()),
        "name": name,
        "dataset": dataset,
        "cron": cron,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    report_jobs.append(job)
    return job


def archive_reports(label: str, report_keys: list[str]) -> str:
    """Bundle a set of generated reports into a single gzip archive.

    Uses the system ``tar`` so the archive metadata (timestamps, ownership)
    matches what operators expect from the CLI tooling. Returns the archive
    path on disk.
    """
    archive_path = storage.resolve_key(f"{label}.tar.gz", root=storage.REPORTS_ROOT)
    members = " ".join(
        storage.resolve_key(key, root=storage.REPORTS_ROOT) for key in report_keys
    )
    command = f"tar -czf {archive_path} {members}"
    subprocess.run(command, shell=True, check=False)
    return archive_path
