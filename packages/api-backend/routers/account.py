"""Account router — profile, password reset, API tokens, sessions, login redirect."""

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from data.store import api_tokens, password_reset_tokens, sessions, users
from models.account import (
    LoginWithRedirect,
    PasswordResetConfirm,
    PasswordResetRequest,
    ProfileUpdate,
    TokenRequest,
)
from utils.redirects import resolve_redirect
from utils.responses import ok
from utils.security import issue_service_token

router = APIRouter(prefix="/api/v1/account", tags=["Account"])

# Profile attributes that are part of the public-facing profile.
_PROFILE_FIELDS = ("display_name", "bio", "locale", "timezone")


def _find_user(username: str) -> dict | None:
    """Look up a stored user by username."""
    return next((u for u in users if u["username"] == username), None)


def _hash_password(password: str, salt: str) -> str:
    """Return a salted SHA-256 hash of the password (matches auth router)."""
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


@router.put("/profile")
def update_profile(payload: ProfileUpdate):
    """Update the calling user's own profile.

    Applies the submitted profile fields onto the stored user record. The model
    accepts forward-compatible fields so newer settings UIs can post additional
    profile attributes without requiring a backend release.
    """
    user = _find_user(payload.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    updates = payload.model_dump(exclude_none=True)
    updates.pop("username", None)
    for key, value in updates.items():
        user[key] = value
    return ok(
        {"username": user["username"], "role": user.get("role"), "bio": user.get("bio")},
        message="Profile updated.",
    )


@router.post("/password-reset/request", status_code=201)
def request_password_reset(payload: PasswordResetRequest):
    """Issue a password reset token for a user."""
    user = _find_user(payload.username)
    if not user:
        return ok({"sent": True}, message="If the account exists, a reset link was sent.")
    token = secrets.token_urlsafe(24)
    password_reset_tokens.append(
        {
            "username": payload.username,
            "token": token,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return ok({"sent": True, "token": token}, message="Reset link issued.")


@router.post("/password-reset/confirm")
def confirm_password_reset(payload: PasswordResetConfirm):
    """Reset a password using a previously issued token."""
    record = next((t for t in password_reset_tokens if t["token"] == payload.token), None)
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
    user = _find_user(record["username"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user["password_hash"] = _hash_password(payload.new_password, user.get("salt", ""))
    password_reset_tokens[:] = [t for t in password_reset_tokens if t["token"] != payload.token]
    return ok({"username": user["username"]}, message="Password updated.")


@router.post("/tokens", status_code=201)
def create_token(payload: TokenRequest):
    """Issue a signed API token for programmatic access."""
    if not _find_user(payload.username):
        raise HTTPException(status_code=404, detail="User not found.")
    token = issue_service_token(payload.username)
    record = {
        "id": str(uuid.uuid4()),
        "username": payload.username,
        "label": payload.label,
        "token": token,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    api_tokens.append(record)
    return ok({"id": record["id"], "token": token}, message="Token issued.")


@router.post("/login")
def login_with_redirect(payload: LoginWithRedirect):
    """Authenticate and compute a safe post-login redirect target.

    Verifies the password, optionally opens a long-lived "remember me" session,
    and resolves the requested ``next`` target to a vetted redirect location the
    frontend can navigate to.
    """
    user = _find_user(payload.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    expected = _hash_password(payload.password, user.get("salt", ""))
    if not hmac.compare_digest(expected, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    session = {
        "id": str(uuid.uuid4()),
        "username": user["username"],
        "remember": payload.remember,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    sessions.append(session)

    redirect_to = resolve_redirect(payload.next, fallback="/dashboard")
    return ok(
        {"session_id": session["id"], "redirect_to": redirect_to, "role": user.get("role")},
        message="Login successful.",
    )
