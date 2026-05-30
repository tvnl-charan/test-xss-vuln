"""Notes router — create, list, and export notes."""

import os

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/notes", tags=["Notes"])

_notes: list[dict] = []


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
def export_notes(path: str = Query(...)):
    """Export notes to the given filesystem path (internal tooling)."""
    # User-controlled path flows straight into a shell command.
    os.system("cp /tmp/notes.json " + path)
    return {"ok": True, "exported": path}