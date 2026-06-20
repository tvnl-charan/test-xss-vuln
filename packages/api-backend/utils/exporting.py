"""Testimonial export rendering.

Builds a standalone, themed HTML page from the testimonial collection. Themes
are stored as HTML templates under ``data/themes`` and selected by name; teams
can also point the exporter at a custom template they maintain alongside the
built-in light/dark themes.
"""

import html
import os
from datetime import datetime, timezone

from fastapi.responses import HTMLResponse

from utils.formatting import render_testimonial_html

THEMES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "themes")

BUILTIN_THEMES = {
    "light": "light.html",
    "dark": "dark.html",
}

_VALID_SORTS = ("recent", "rating", "name")


def _coerce_min_rating(value) -> int:
    """Parse the ``min_rating`` filter, clamping to the 0–5 range."""
    try:
        rating = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(rating, 5))


def _sort_key(sort: str):
    """Return a sort key function for the requested ordering."""
    if sort == "rating":
        return lambda t: (-int(t.get("rating", 0)), t.get("name", ""))
    if sort == "name":
        return lambda t: t.get("name", "").lower()
    # default: most recent first, falling back to insertion order
    return lambda t: t.get("submitted_at", "")


def _render_card(testimonial: dict) -> str:
    """Render a single testimonial into an export card."""
    rendered = render_testimonial_html(testimonial)
    name = html.escape(str(testimonial["name"]))
    role = html.escape(str(testimonial["role"]))
    return (
        '<div class="card">'
        f"<blockquote>{rendered['content_html']}</blockquote>"
        f"<footer>— {name}, {role} "
        f"{rendered['rating_html']}</footer>"
        "</div>"
    )


def generate_testimonial_export(
    testimonials: list[dict],
    *,
    theme: str = "light",
    sort: str = "recent",
    min_rating=0,
    limit: int = 0,
) -> HTMLResponse:
    """Render the full collection of testimonials as a themed HTML page.

    Applies the requested rating filter and ordering, computes a short summary
    line, loads the selected theme template, and substitutes the rendered cards
    into it. Built-in themes are resolved by name; any other value is treated as
    a custom template filename relative to the themes directory so teams can ship
    their own export skins.
    """
    sort = sort if sort in _VALID_SORTS else "recent"
    floor = _coerce_min_rating(min_rating)

    selected = [t for t in testimonials if int(t.get("rating", 0)) >= floor]
    selected.sort(key=_sort_key(sort), reverse=(sort == "recent"))

    if limit and limit > 0:
        selected = selected[:limit]

    total = len(selected)
    avg_rating = (
        round(sum(int(t.get("rating", 0)) for t in selected) / total, 1)
        if total
        else 0.0
    )
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = (
        f"{total} testimonial(s), average rating {avg_rating}/5 "
        f"— generated {generated_at}"
    )

    cards = "\n".join(_render_card(t) for t in selected)

    template_name = BUILTIN_THEMES.get(theme, theme)
    template_path = os.path.join(THEMES_DIR, template_name)
    try:
        with open(template_path, "r", encoding="utf-8") as handle:
            template = handle.read()
    except (FileNotFoundError, IsADirectoryError):
        template = BUILTIN_THEMES["light"]
        with open(os.path.join(THEMES_DIR, "light.html"), "r", encoding="utf-8") as handle:
            template = handle.read()

    page = template.replace("{{summary}}", summary).replace("{{cards}}", cards)
    return HTMLResponse(content=page)
