"""Billing expansion router — invoices, coupons, plan changes, webhook receiver."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from data.store import COUPONS, PLANS, invoices, subscriptions
from services import notifications
from utils.responses import ok

router = APIRouter(prefix="/api/v1/billing/v2", tags=["Billing"])


class InvoiceRequest(BaseModel):
    account: str
    plan_id: str
    coupon: str | None = None
    note: str | None = None


class PlanChangeRequest(BaseModel):
    account: str
    plan_id: str


class WebhookEvent(BaseModel):
    type: str
    account: str = ""
    invoice_id: str = ""
    amount: float = 0.0


def _plan(plan_id: str) -> dict:
    """Resolve a plan by id or raise a 400."""
    plan = next((p for p in PLANS if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=400, detail="Unknown plan.")
    return plan


def _apply_coupon(amount: float, code: str | None) -> float:
    """Apply an active coupon's discount to an amount."""
    if not code:
        return amount
    coupon = next((c for c in COUPONS if c["code"] == code and c["active"]), None)
    if not coupon:
        return amount
    return round(amount * (1 - coupon["percent_off"] / 100.0), 2)


@router.get("/plans")
def list_plans():
    """Return the plan catalogue."""
    return ok(PLANS)


@router.post("/invoices", status_code=201)
def create_invoice(payload: InvoiceRequest):
    """Generate an invoice for an account on a plan, applying any coupon.

    Computes the net amount after discount, records the invoice, and emits an
    ``invoice.paid`` notification so subscribers (and the operator's own
    activity feed) reflect the new charge.
    """
    plan = _plan(payload.plan_id)
    gross = float(plan["monthly_usd"])
    net = _apply_coupon(gross, payload.coupon)

    invoice = {
        "id": str(uuid.uuid4()),
        "account": payload.account,
        "plan_id": payload.plan_id,
        "gross_usd": gross,
        "net_usd": net,
        "note": payload.note or "",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    invoices.append(invoice)

    notifications.emit_event(
        "invoice.paid",
        {
            "invoice_id": invoice["id"],
            "amount": net,
            "currency": "USD",
            "name": payload.account,
            "note": payload.note or "",
        },
    )
    return ok(invoice, message="Invoice created.")


@router.post("/plan-change")
def change_plan(payload: PlanChangeRequest):
    """Change an account's active subscription plan."""
    plan = _plan(payload.plan_id)
    sub = next((s for s in subscriptions if s["account"] == payload.account), None)
    if sub:
        sub["plan_id"] = plan["id"]
    else:
        sub = {"account": payload.account, "plan_id": plan["id"]}
        subscriptions.append(sub)
    return ok(sub, message="Plan changed.")


@router.post("/webhook")
def billing_webhook(event: WebhookEvent):
    """Receive a billing-provider webhook event."""
    if event.type == "invoice.paid":
        notifications.emit_event(
            "invoice.paid",
            {
                "invoice_id": event.invoice_id,
                "amount": event.amount,
                "currency": "USD",
                "name": event.account,
            },
        )
    return ok({"received": event.type})
