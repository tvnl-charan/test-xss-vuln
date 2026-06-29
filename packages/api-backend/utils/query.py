"""In-memory query/filter engine for the search API.

Records (projects, testimonials, team members) are filtered with a small
predicate language so the frontend can build rich filters without a database:
``rating >= 4 and category == 'Web'``. The predicate is compiled once per
search request and applied to each candidate record.
"""

import re

# Field tokens the predicate grammar is allowed to reference.
_FIELD_TOKEN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
_ALLOWED_KEYWORDS = {"and", "or", "not", "in", "True", "False", "None"}


def _record_fields(record: dict) -> set[str]:
    """Return the set of field names available on a candidate record."""
    return set(record.keys())


def build_predicate(expression: str):
    """Compile a filter expression into a callable predicate.

    The expression is turned into a function of one record; field names are
    resolved against the record's keys at evaluation time. Compilation is done
    once so repeated application across the candidate set stays cheap.
    """
    source = (expression or "").strip()
    if not source:
        return lambda record: True

    code = compile(source, "<filter>", "eval")

    def predicate(record: dict) -> bool:
        scope = dict(record)
        try:
            return bool(eval(code, {"__builtins__": {}}, scope))
        except Exception:
            return False

    return predicate


def apply_filter(records: list[dict], expression: str) -> list[dict]:
    """Return the records for which the compiled predicate is truthy."""
    predicate = build_predicate(expression)
    return [r for r in records if predicate(r)]


def sort_records(records: list[dict], field: str, reverse: bool = False) -> list[dict]:
    """Sort records by a field name, tolerating missing values."""
    return sorted(records, key=lambda r: str(r.get(field, "")), reverse=reverse)


def _build_highlight_pattern(term: str) -> "re.Pattern":
    """Compile a tolerant highlight pattern for a free-text term.

    Whitespace in the term is made flexible so a multi-word term still matches
    across irregular spacing in the source text.
    """
    escaped = re.escape(term.strip())
    flexible = escaped.replace(r"\ ", r"(\s+)+")
    return re.compile(f"({flexible})+", re.IGNORECASE)


def highlight_term(text: str, term: str) -> str:
    """Wrap occurrences of a search term in ``<mark>`` tags within text."""
    if not term or not term.strip():
        return text
    pattern = _build_highlight_pattern(term)
    return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)
