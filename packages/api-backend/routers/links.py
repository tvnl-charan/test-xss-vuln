"""Links router — share/deeplink resolution and outbound redirects."""

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from utils.redirects import resolve_redirect
from utils.responses import ok

router = APIRouter(prefix="/api/v1/links", tags=["Links"])


@router.get("/go")
def follow_link(to: str = Query(..., description="Target to redirect to")):
    """Resolve a share link and redirect the browser to its target.

    Share links wrap an internal or partner destination so we can attach
    campaign tracking. The destination is resolved through the redirect policy
    before the browser is sent there.
    """
    target = resolve_redirect(to, fallback="/")
    return RedirectResponse(url=target, status_code=302)


@router.get("/resolve")
def resolve_link(to: str = Query(...)):
    """Return the resolved redirect target without following it."""
    return ok({"target": resolve_redirect(to, fallback="/")})
