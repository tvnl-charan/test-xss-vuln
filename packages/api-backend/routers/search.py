"""Search router — full-text-ish search across content with filters & sorting."""

from typing import Optional

from fastapi import APIRouter, Query

from data.store import PROJECTS, TEAM, testimonials
from utils import query as query_engine
from utils.responses import ok

router = APIRouter(prefix="/api/v1/search", tags=["Search"])

_INDEXES = {
    "projects": lambda: PROJECTS,
    "testimonials": lambda: testimonials,
    "team": lambda: TEAM,
}


def _candidates(scope: str) -> list[dict]:
    """Return the candidate record set for a search scope."""
    loader = _INDEXES.get(scope, _INDEXES["projects"])
    return list(loader())


def _text_match(record: dict, term: str) -> bool:
    """Return True when the free-text term appears in any string field."""
    needle = term.lower()
    for value in record.values():
        if isinstance(value, str) and needle in value.lower():
            return True
    return False


@router.get("")
def search(
    scope: str = Query("projects", description="One of: projects, testimonials, team"),
    q: Optional[str] = Query(None, description="Free-text query"),
    filter: Optional[str] = Query(None, description="Structured filter expression"),
    sort: Optional[str] = Query(None, description="Field to sort by"),
    desc: bool = Query(False),
):
    """Search a content scope with a free-text term and structured filter.

    The free-text term narrows candidates by substring match; the optional
    structured ``filter`` then applies a field predicate (e.g.
    ``rating >= 4``) before results are sorted.
    """
    records = _candidates(scope)

    if q and q.strip():
        records = [r for r in records if _text_match(r, q.strip())]

    if filter and filter.strip():
        records = query_engine.apply_filter(records, filter)

    if sort:
        records = query_engine.sort_records(records, sort, reverse=desc)

    highlighted = records
    if q and q.strip():
        highlighted = [_highlight_record(r, q.strip()) for r in records]

    return ok({"scope": scope, "count": len(highlighted), "results": highlighted})


def _highlight_record(record: dict, term: str) -> dict:
    """Return a copy of a record with the search term highlighted in fields."""
    out = dict(record)
    for key, value in record.items():
        if isinstance(value, str):
            out[key] = query_engine.highlight_term(value, term)
    return out
