"""Slugify helper (main-branch utility)."""

import re

_NON_WORD = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Lowercase *text* and collapse non-word runs into single hyphens."""
    return _NON_WORD.sub("-", text.strip().lower()).strip("-")