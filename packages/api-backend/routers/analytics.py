"""Analytics router — evaluate custom report formulas."""

from fastapi import APIRouter
from pydantic import BaseModel

from utils import reporting_engine
from utils.responses import ok

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


class FormulaRequest(BaseModel):
    formula: str


@router.post("/evaluate")
def evaluate_report(payload: FormulaRequest):
    """Evaluate a custom analyst report formula over the dataset."""
    result = reporting_engine.dispatch_formula(payload.formula)
    return ok(result, message="Formula evaluated.")
