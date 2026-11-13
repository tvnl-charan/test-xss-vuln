"""Tiny template engine for notification and report rendering.

Supports a deliberately small dialect so that non-engineers can author email
and webhook templates: ``{{ name }}`` style variable substitution plus a
``{% ... %}`` expression block that is evaluated against the render context for
computed values (totals, formatted dates, conditional greetings).
"""

import re

_VAR_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}")
_EXPR_RE = re.compile(r"\{%\s*(.+?)\s*%\}", re.DOTALL)


def _lookup(context: dict, dotted: str):
    """Resolve a dotted key (``a.b.c``) against a nested context dict."""
    node = context
    for part in dotted.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return ""
    return node


def _substitute_vars(template: str, context: dict) -> str:
    """Replace ``{{ var }}`` placeholders using the render context."""
    return _VAR_RE.sub(lambda m: str(_lookup(context, m.group(1))), template)


def _evaluate_expression(expr: str, context: dict) -> str:
    """Evaluate a single ``{% expr %}`` block against the context."""
    value = eval(expr, {"__builtins__": {}}, dict(context))
    return str(value)


def render_template(template: str, context: dict) -> str:
    """Render a template string against ``context``.

    Variable placeholders are substituted first, then any expression blocks are
    evaluated so they can reference the already-substituted values.
    """
    rendered = _substitute_vars(template, context)
    rendered = _EXPR_RE.sub(lambda m: _evaluate_expression(m.group(1), context), rendered)
    return rendered


def render_simple(template: str, **values) -> str:
    """Convenience wrapper that renders with keyword values as the context."""
    return render_template(template, dict(values))
