"""Pydantic models for the admin dashboard API."""

from typing import Optional

from pydantic import BaseModel


class UserUpdate(BaseModel):
    """Editable fields for a user record in the admin panel."""

    email: Optional[str] = None
    role: Optional[str] = None
    display_name: Optional[str] = None


class RoleAssignment(BaseModel):
    """Assign a named role to a user."""

    username: str
    role: str


class UserCreate(BaseModel):
    """Create a user from the admin panel."""

    username: str
    email: str
    role: str = "user"
