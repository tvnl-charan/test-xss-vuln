"""
Authentication middleware — JWT validation and API key checking.

Provides dependency functions for FastAPI route protection.
"""

import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Header, Request

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_MINUTES, ADMIN_API_KEY


def create_jwt_token(user_id: str, role: str = "user") -> str:
    """Create a signed JWT token for a user."""
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises on invalid/expired."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Extract the current user from the Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization[7:]
    return decode_jwt_token(token)


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Require that the current user has admin role."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def validate_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Validate an API key from the X-API-Key header."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True
