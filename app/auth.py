import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import HTTPException, Request, status

JWT_SECRET = os.environ.get("JWT_SECRET", "alumni-track-super-secret-dev-key-2026")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.environ.get("JWT_EXPIRE_HOURS", "24"))

VALID_ROLES = {"graduate", "admin"}


def hash_password(plain_password: str) -> str:
    """Hashes a plaintext password with bcrypt and a random salt ($2b$12$...)."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: Optional[str]) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash. Never uses ==."""
    if not plain_password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(user: dict, expires_hours: Optional[int] = None) -> str:
    """
    Creates a signed JWT containing only non-secret identity claims:
    sub (user id), name, email, role, iat, exp.
    """
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=expires_hours or JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(user["id"]),
        "id": int(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user.get("role", "graduate"),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT. Returns user claims dict or None if invalid/expired."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("id") or (int(payload["sub"]) if "sub" in payload else None)
        if user_id is None:
            return None
        return {
            "id": int(user_id),
            "name": payload.get("name", ""),
            "email": payload.get("email", ""),
            "role": payload.get("role", "graduate"),
        }
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError, TypeError):
        return None


def extract_token_from_request(request: Request) -> Optional[str]:
    """Extracts JWT from Authorization: Bearer <token> header or access_token cookie."""
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.strip().split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1].strip():
            return parts[1].strip()
        # Present but malformed Authorization header -> return sentinel invalid token
        return "__INVALID_AUTH_HEADER__"

    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token.strip()

    return None


def get_current_user_optional(request: Request) -> Optional[dict]:
    """Returns the authenticated user dict attached by AuthMiddleware, or None for guest."""
    return getattr(request.state, "user", None)


def require_auth(request: Request) -> dict:
    """FastAPI dependency: ensures the request is authenticated (401 otherwise)."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="login required",
        )
    return user


def require_admin(request: Request) -> dict:
    """FastAPI dependency: ensures the request is from an admin (401 if guest, 403 if not admin)."""
    user = require_auth(request)
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not allowed",
        )
    return user
