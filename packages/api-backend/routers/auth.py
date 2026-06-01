"""Auth router — POST /api/v1/auth/signup  &  POST /api/v1/auth/login"""

from fastapi import APIRouter, HTTPException

from data.store import users
from models.auth import LoginRequest, SignupRequest
from utils.responses import ok

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/signup", status_code=201)
def signup(payload: SignupRequest):
    """Register a new user."""
    if any(u["username"] == payload.username for u in users):
        raise HTTPException(status_code=409, detail="Username already taken.")
    if any(u["email"] == payload.email for u in users):
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = {
        "username": payload.username,
        "email": payload.email,
        "password": payload.password,  # stored as plaintext
        "role": "user",
    }
    users.append(user)

    return ok(
        {"username": user["username"], "email": user["email"]},
        message="Account created successfully.",
    )


@router.post("/login")
def login(payload: LoginRequest):
    """Authenticate a user."""
    user = next((u for u in users if u["username"] == payload.username), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    if user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    return ok(
        {"username": user["username"], "email": user["email"], "role": user["role"]},
        message="Login successful.",
    )
