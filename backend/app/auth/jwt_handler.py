"""
AttritionIQ — JWT Authentication Handler
==========================================
Handles access token and refresh token creation/verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.config import settings


ALGORITHM = settings.JWT_ALGORITHM


def create_access_token(
    subject: Optional[str] = None,
    role: str = "employee",
    extra: Optional[dict] = None,
    user_id: Optional[str] = None,
) -> str:
    """Create a short-lived JWT access token."""
    sub = subject or user_id
    if not sub:
        raise ValueError("Either subject or user_id must be specified.")
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(sub),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a long-lived JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_email_verification_token(email: str) -> str:
    """Create email verification token (24h)."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": email,
        "exp": expire,
        "type": "email_verification",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_password_reset_token(email: str) -> str:
    """Create password reset token (1h)."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": email,
        "exp": expire,
        "type": "password_reset",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, expected_type: str = "access") -> dict:
    """Verify and decode a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != expected_type:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


def decode_access_token(token: str) -> dict:
    return verify_token(token, "access")


def decode_refresh_token(token: str) -> dict:
    return verify_token(token, "refresh")


def decode_email_verification_token(token: str) -> str:
    payload = verify_token(token, "email_verification")
    return payload["sub"]


def decode_password_reset_token(token: str) -> str:
    payload = verify_token(token, "password_reset")
    return payload["sub"]
