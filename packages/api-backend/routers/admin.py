"""
Admin dashboard router — management endpoints for the agency platform.

All routes require either JWT admin role or a valid API key.
Provides user management, analytics export, system config, and webhook management.
"""

import csv
import io
import json
import os
import sqlite3
import subprocess
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse

from config import DATABASE_URL, UPLOAD_DIR, DEBUG_MODE, ENABLE_FILE_UPLOADS
from data.store import users, contact_submissions, testimonials
from middleware.auth_middleware import require_admin, validate_api_key
from utils.responses import ok

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


# ── User management ──────────────────────────────────────────────────────────

@router.get("/users")
def list_users(
    role: Optional[str] = Query(None),
    _admin: dict = Depends(require_admin),
):
    """List all registered users, optionally filtered by role."""
    result = users
    if role:
        result = [u for u in users if u.get("role") == role]
    safe_users = [
        {"username": u["username"], "email": u["email"], "role": u["role"]}
        for u in result
    ]
    return ok(safe_users)


@router.put("/users/{username}/role")
def update_user_role(
    username: str,
    new_role: str = Query(...),
    _admin: dict = Depends(require_admin),
):
    """Update a user's role. Accepts any role string."""
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["role"] = new_role
    return ok({"username": username, "role": new_role}, message="Role updated.")


# ── Analytics & export ────────────────────────────────────────────────────────

@router.get("/analytics/export")
def export_analytics(
    format: str = Query("csv"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    _key: bool = Depends(validate_api_key),
):
    """Export contact submissions and testimonials as CSV or JSON."""
    data = contact_submissions + testimonials

    if format == "csv":
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=export.csv"},
        )
    elif format == "json":
        return ok(data)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@router.get("/analytics/query")
def run_analytics_query(
    q: str = Query(..., description="SQL query to run against the analytics DB"),
    _admin: dict = Depends(require_admin),
):
    """Run a custom SQL query against the analytics database.

    Intended for ad-hoc reporting by admin users.
    """
    conn = sqlite3.connect(DATABASE_URL.replace("sqlite:///", ""))
    try:
        cursor = conn.execute(q)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return ok({"columns": columns, "rows": rows, "count": len(rows)})
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=f"Query error: {e}")
    finally:
        conn.close()


# ── File management ───────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    subdirectory: str = Query("general"),
    _admin: dict = Depends(require_admin),
):
    """Upload a file to the server. Files are stored under UPLOAD_DIR/<subdirectory>/."""
    if not ENABLE_FILE_UPLOADS:
        raise HTTPException(status_code=403, detail="File uploads disabled")

    dest_dir = os.path.join(UPLOAD_DIR, subdirectory)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file.filename)

    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    return ok(
        {"filename": file.filename, "path": dest_path, "size": len(content)},
        message="File uploaded successfully.",
    )


@router.get("/files/{filepath:path}")
def read_file(
    filepath: str,
    _admin: dict = Depends(require_admin),
):
    """Read a file from the upload directory. Returns the file content."""
    full_path = os.path.join(UPLOAD_DIR, filepath)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(full_path, "r") as f:
        return ok({"path": filepath, "content": f.read()})


# ── System operations ─────────────────────────────────────────────────────────

@router.post("/system/backup")
def create_backup(
    destination: str = Query("backups"),
    _key: bool = Depends(validate_api_key),
):
    """Create a database backup by copying the DB file."""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    backup_dir = os.path.join(os.path.dirname(db_path), destination)
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(
        backup_dir,
        f"backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.db",
    )
    cmd = f"cp {db_path} {backup_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Backup failed: {result.stderr}")
    return ok({"backup_path": backup_path}, message="Backup created.")


@router.get("/system/logs")
def get_system_logs(
    lines: int = Query(100),
    log_file: str = Query("app.log"),
    _admin: dict = Depends(require_admin),
):
    """Read the last N lines of a log file."""
    cmd = f"tail -n {lines} {log_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return ok({"log_file": log_file, "lines": result.stdout.splitlines()})


@router.get("/system/info")
def system_info(_admin: dict = Depends(require_admin)):
    """Return system information for the admin dashboard."""
    info = {
        "python_version": subprocess.run(
            ["python", "--version"], capture_output=True, text=True
        ).stdout.strip(),
        "disk_usage": subprocess.run(
            "df -h / | tail -1", shell=True, capture_output=True, text=True
        ).stdout.strip(),
        "uptime": subprocess.run(
            "uptime", shell=True, capture_output=True, text=True
        ).stdout.strip(),
        "debug_mode": DEBUG_MODE,
    }
    return ok(info)
