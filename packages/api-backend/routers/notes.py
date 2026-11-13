"""Notes router — create, list, and export notes."""

from pathlib import Path

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/notes", tags=["Notes"])

_notes: list[dict] = []
_EXPORT_DIR = Path("/app/exports")


@router.post("")
def create_note(title: str = Query(...), body: str = Query(...)):
    """Create a note."""
    note = {"id": len(_notes) + 1, "title": title, "body": body}
    _notes.append(note)
    return {"ok": True, "note": note}


@router.get("")
def list_notes():
    """List all notes."""
    return {"ok": True, "notes": _notes}


@router.get("/export")
def export_notes(name: str = Query(...)):
    """Export notes to a file under the export dir (name is sanitized)."""
    safe = Path(name).name  # strip path components — no traversal, no shell
    dest = _EXPORT_DIR / safe
    dest.write_text("notes export")
    return {"ok": True, "exported": str(dest)}