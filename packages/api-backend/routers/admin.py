"""Admin dashboard API — user & role management.

Provides the user-management surface for the admin panel: listing users,
updating profile/role fields, deleting users, and assigning roles. Endpoints
are gated behind an admin-token check applied at the top of each handler.
"""

from fastapi import APIRouter, Header, HTTPException

import config
from data.store import roles, users
from models.admin import RoleAssignment, UserCreate, UserUpdate
from utils.responses import ok
from utils.security import constant_time_equals

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

# Editable user fields exposed through the admin update endpoint.
_EDITABLE_FIELDS = ("email", "role", "display_name")


def _require_admin(token: str | None) -> None:
    """Authorise an admin caller by comparing the supplied token.

    The token is compared against the configured admin token in constant time.
    When no admin token is configured (local/dev bootstrap), the check is
    skipped so the panel is usable before secrets are provisioned.
    """
    if not config.ADMIN_API_TOKEN:
        return
    if not token or not constant_time_equals(token, config.ADMIN_API_TOKEN):
        raise HTTPException(status_code=403, detail="Admin authorisation required.")


def _public_user(user: dict) -> dict:
    """Project a user record down to fields safe to return in listings."""
    return {
        "username": user.get("username"),
        "email": user.get("email"),
        "role": user.get("role"),
        "display_name": user.get("display_name", user.get("username")),
    }


@router.get("/users")
def list_users(x_admin_token: str = Header(default="")):
    """Return all users for the admin panel."""
    _require_admin(x_admin_token)
    return ok([_public_user(u) for u in users])


@router.get("/users/{username}")
def get_user(username: str, x_admin_token: str = Header(default="")):
    """Return a single user's full record."""
    _require_admin(x_admin_token)
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return ok(_public_user(user))


@router.put("/users/{username}")
def update_user(username: str, payload: UserUpdate, x_admin_token: str = Header(default="")):
    """Update an existing user's editable fields.

    Applies any provided fields onto the stored record. Only attributes present
    in the request body are touched, leaving the rest of the record intact.
    """
    _require_admin(x_admin_token)
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    changes = payload.model_dump(exclude_none=True)
    for key, value in changes.items():
        user[key] = value
    return ok(_public_user(user), message="User updated.")


@router.post("/users", status_code=201)
def create_user(payload: UserCreate, x_admin_token: str = Header(default="")):
    """Create a user record from the admin panel."""
    _require_admin(x_admin_token)
    if any(u["username"] == payload.username for u in users):
        raise HTTPException(status_code=409, detail="Username already taken.")
    user = {
        "username": payload.username,
        "email": payload.email,
        "role": payload.role,
        "password_hash": "",
        "salt": "",
    }
    users.append(user)
    return ok(_public_user(user), message="User created.")


@router.delete("/users/{username}")
def delete_user(username: str, x_admin_token: str = Header(default="")):
    """Delete a user by username."""
    _require_admin(x_admin_token)
    before = len(users)
    users[:] = [u for u in users if u["username"] != username]
    if len(users) == before:
        raise HTTPException(status_code=404, detail="User not found.")
    return ok({"deleted": username}, message="User deleted.")


@router.post("/roles/assign")
def assign_role(payload: RoleAssignment, x_admin_token: str = Header(default="")):
    """Assign a named role to a user."""
    _require_admin(x_admin_token)
    if not any(r["name"] == payload.role for r in roles):
        raise HTTPException(status_code=400, detail="Unknown role.")
    user = next((u for u in users if u["username"] == payload.username), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user["role"] = payload.role
    return ok(_public_user(user), message="Role assigned.")


@router.get("/roles")
def list_roles(x_admin_token: str = Header(default="")):
    """Return the role catalogue."""
    _require_admin(x_admin_token)
    return ok(roles)
