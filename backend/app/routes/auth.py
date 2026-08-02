"""
AttritionIQ — Authentication Routes
======================================
Login, Register, Refresh, Logout, Verify Email,
Forgot Password, Reset Password.
"""

from datetime import datetime, timezone
from typing import Annotated

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_email_verification_token,
    decode_password_reset_token,
    decode_refresh_token,
)
from app.auth.password import hash_password, verify_password
from app.auth.rbac import get_current_active_user
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    VerifyEmailRequest,
)
from app.utils.audit import log_audit

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Register a new user account."""

    # Check email uniqueness
    result = await db.execute(select(User).where(User.email == user_data.email.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Check username uniqueness
    result = await db.execute(select(User).where(User.username == user_data.username.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    # Create user
    verification_token = create_email_verification_token(user_data.email)
    user = User(
        email=user_data.email.lower(),
        username=user_data.username.lower(),
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role="viewer",
        status="pending_verification",
        email_verification_token=verification_token,
    )
    db.add(user)
    await db.flush()

    # Send verification email in background
    if settings.EMAIL_ENABLED:
        background_tasks.add_task(
            send_verification_email, user.email, user.full_name, verification_token
        )

    await db.commit()
    await db.refresh(user)

    logger.info("User registered", user_id=str(user.id), email=user.email)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user and return JWT tokens."""

    # Find user by email or username
    result = await db.execute(
        select(User).where(
            (User.email == form_data.username.lower()) |
            (User.username == form_data.username.lower())
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        await log_audit(db, None, "login", description="Failed login attempt", ip_address=request.client.host)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email first")

    # Generate tokens
    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))

    # Update user
    await db.execute(
        update(User).where(User.id == user.id).values(
            last_login_at=datetime.now(timezone.utc),
            refresh_token=refresh_token,
        )
    )
    await db.commit()
    await log_audit(db, user.id, "login", description="Successful login", ip_address=request.client.host)

    logger.info("User logged in", user_id=str(user.id))
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token_str: str,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Issue new access token using refresh token."""
    payload = decode_refresh_token(refresh_token_str)
    user_id = payload["sub"]

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or user.refresh_token != refresh_token_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access_token = create_access_token(str(user.id), user.role)
    new_refresh_token = create_refresh_token(str(user.id))

    await db.execute(
        update(User).where(User.id == user.id).values(refresh_token=new_refresh_token)
    )
    await db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user=user,
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Invalidate refresh token on logout."""
    await db.execute(
        update(User).where(User.id == current_user.id).values(refresh_token=None)
    )
    await db.commit()
    await log_audit(db, current_user.id, "logout")
    return {"success": True, "message": "Logged out successfully"}


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Verify user email with token."""
    email = decode_email_verification_token(request.token)

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_verified:
        return {"success": True, "message": "Email already verified"}

    await db.execute(
        update(User).where(User.id == user.id).values(
            is_verified=True,
            status="active",
            email_verified_at=datetime.now(timezone.utc),
            email_verification_token=None,
        )
    )
    await db.commit()
    return {"success": True, "message": "Email verified successfully. You can now log in."}


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Send password reset email."""
    result = await db.execute(select(User).where(User.email == request.email.lower()))
    user = result.scalar_one_or_none()

    # Always return 200 to prevent email enumeration
    if user and settings.EMAIL_ENABLED:
        token = create_password_reset_token(user.email)
        await db.execute(
            update(User).where(User.id == user.id).values(password_reset_token=token)
        )
        await db.commit()
        background_tasks.add_task(send_password_reset_email, user.email, user.full_name, token)

    return {"success": True, "message": "If an account exists, a reset email has been sent"}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Reset password using token."""
    email = decode_password_reset_token(request.token)

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or user.password_reset_token != request.token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    await db.execute(
        update(User).where(User.id == user.id).values(
            hashed_password=hash_password(request.new_password),
            password_reset_token=None,
            password_reset_expires_at=None,
        )
    )
    await db.commit()
    return {"success": True, "message": "Password reset successfully. Please log in."}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current user profile."""
    return current_user


# ========================
# Email helpers (stubs — wired to fastapi-mail)
# ========================
async def send_verification_email(email: str, name: str, token: str) -> None:
    logger.info("Sending verification email", email=email)


async def send_password_reset_email(email: str, name: str, token: str) -> None:
    logger.info("Sending password reset email", email=email)
