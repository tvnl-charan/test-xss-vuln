"""Pydantic models for account / auth-hardening endpoints."""

from pydantic import BaseModel, ConfigDict


class ProfileUpdate(BaseModel):
    """Self-service profile update.

    Extra keys are preserved so the settings UI can post forward-compatible
    fields (locale, timezone, notification opt-ins) without an API change.
    """

    model_config = ConfigDict(extra="allow")

    username: str
    display_name: str | None = None
    bio: str | None = None


class PasswordResetRequest(BaseModel):
    username: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class TokenRequest(BaseModel):
    username: str
    label: str = "default"


class LoginWithRedirect(BaseModel):
    username: str
    password: str
    next: str = "/"
    remember: bool = False
