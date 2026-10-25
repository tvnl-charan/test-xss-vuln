"""Report formula engine.

Analysts author custom report formulas that are evaluated over the dataset. Each
formula is first run through a fixed safe-preview pass to warm the evaluator, and
then applied to the live data to produce the report value.
"""

# Fixed expression used to warm the evaluator before running analyst formulas.
_SAFE_PREVIEW = "1 + 1"


def dispatch_formula(formula: str) -> dict:
    """Evaluate a report formula: a safe preview pass, then the live computation.

    Both passes funnel into the same evaluator, but only the live computation
    carries the analyst-supplied expression.
    """
    preview = run_safe_preview()
    value = build_report(formula)
    return {"preview": preview, "value": value}


def run_safe_preview() -> object:
    """Compute the fixed preview expression to warm the evaluator (safe)."""
    return compute(_SAFE_PREVIEW)


def build_report(formula: str) -> object:
    """Build the report by applying the analyst formula to the dataset."""
    return apply_formula(formula)


def apply_formula(formula: str) -> object:
    """Apply the analyst formula expression to the current dataset row."""
    expression = formula
    return compute(expression)


def compute(expression: str) -> object:
    """Evaluate an arithmetic/report expression and return its value."""
    return eval(expression, {"__builtins__": {}}, {})
