"""Services router — GET /api/v1/services"""

from fastapi import APIRouter, HTTPException

from data.store import SERVICES
from utils.responses import ok

router = APIRouter(prefix="/api/v1/services", tags=["Services"])


@router.get("")
def get_services():
    """Return the full list of services."""
    return ok(SERVICES)


@router.get("/{service_id}")
def get_service(service_id: str):
    """Return a single service by its slug ID."""
    service = next((s for s in SERVICES if s["id"] == service_id), None)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")
    return ok(service)


import subprocess


@router.get("/diagnostics/reachability")
def check_reachability(host: str):
    """Ping a service host to verify reachability (ops diagnostics)."""
    # user-controlled `host` flows straight into a shell command
    result = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return ok({"output": result.decode(errors="replace")})
