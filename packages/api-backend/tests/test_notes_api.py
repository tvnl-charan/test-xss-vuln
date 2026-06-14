"""Tests for the notes router and the shared response envelopes."""

from routers.notes import create_note, list_notes
from utils.responses import error, ok


def test_create_then_list_note():
    created = create_note(title="My Note", body="hello world")
    assert created["ok"] is True
    titles = [n["title"] for n in list_notes()["notes"]]
    assert "My Note" in titles


def test_ok_envelope_wraps_data():
    assert ok([1, 2], message="done") == {
        "success": True,
        "message": "done",
        "data": [1, 2],
    }


def test_error_envelope_marks_failure():
    out = error("nope")
    assert out["success"] is False
    assert out["message"] == "nope"
