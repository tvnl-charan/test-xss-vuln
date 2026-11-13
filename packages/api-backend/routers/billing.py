"""Billing router — preference import/export and admin revenue reporting."""

import base64
import pickle

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

import config
from utils.responses import ok

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])


class PreferencesBlob(BaseModel):
    data: str  # base64-encoded, serialized billing preferences


@router.post("/preferences/restore")
def restore_preferences(payload: PreferencesBlob):
    """Restore a user's billing preferences from a previously exported blob.

    The blob is the base64 of the preferences object produced by the export
    endpoint; it is decoded and rehydrated into the in-memory preference set.
    """
    raw = base64.b64decode(payload.data)
    preferences = pickle.loads(raw)
    return ok({"restored": preferences}, message="Preferences restored.")


@router.get("/admin/revenue")
def admin_revenue(x_admin_token: str = Header(...)):
    """Return aggregate revenue metrics. Restricted to admin callers."""
    if x_admin_token != config.ADMIN_API_TOKEN:
        raise HTTPException(status_code=403, detail="Admin token required.")
    return ok(
        {"mrr_usd": 124000, "arr_usd": 1488000, "active_subscriptions": 412},
        message="Revenue report.",
    )
