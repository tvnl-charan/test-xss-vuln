"""Content formatting utilities for testimonials and exports."""

from fastapi.responses import HTMLResponse


def _star_rating(count: int) -> str:
    """Return an HTML star string for the given rating."""
    filled = min(max(count, 0), 5)
    return "★" * filled + "☆" * (5 - filled)


def enrich_content(raw_content: str, author_name: str) -> str:
    """Add a byline and allow basic markup in testimonial content.

    Supports a subset of Markdown-style formatting:
    - **bold** → <strong>
    - *italic* → <em>
    - [link text](url) → <a href="url">
    """
    import re

    text = raw_content
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def render_testimonial_html(testimonial: dict) -> dict:
    """Return a copy of the testimonial with HTML-enriched content."""
    enriched = enrich_content(testimonial["content"], testimonial["name"])
    stars = _star_rating(testimonial.get("rating", 5))
    return {
        **testimonial,
        "content_html": f'<div class="testimonial-body">{enriched}</div>',
        "rating_html": f'<span class="stars">{stars}</span>',
    }


def build_export_page(testimonials: list[dict]) -> HTMLResponse:
    """Build a full HTML page containing all testimonials."""
    cards = []
    for t in testimonials:
        rendered = render_testimonial_html(t)
        card = f"""
        <div class="card">
            <blockquote>{rendered['content_html']}</blockquote>
            <footer>— {t['name']}, {t['role']} {rendered['rating_html']}</footer>
        </div>"""
        cards.append(card)

    body = "\n".join(cards)
    html = f"""<!DOCTYPE html>
<html>
<head><title>Testimonials</title></head>
<body>
<h1>Client Testimonials</h1>
{body}
</body>
</html>"""
    return HTMLResponse(content=html)