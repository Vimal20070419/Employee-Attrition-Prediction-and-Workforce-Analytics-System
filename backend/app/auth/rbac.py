"""
AttritionIQ — RBAC (Role-Based Access Control)
================================================
FastAPI dependencies for protecting routes by user role.
"""

from typing import List
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.jwt_handler import decode_access_token
from app.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Role hierarchy
ROLE_HIERARCHY = {
    "admin": 4,
    "hr_manager": 3,
    "hr_analyst": 2,
    "viewer": 1,
}


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from JWT."""
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the user is active."""
    if current_user.status == "suspended":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended")
    return current_user


def require_roles(*allowed_roles: str):
    """Dependency factory: require one of the specified roles."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}",
            )
        return current_user
    return role_checker


def require_min_role(min_role: str):
    """Dependency factory: require at least a minimum role level."""
    min_level = ROLE_HIERARCHY.get(min_role, 0)
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_level = ROLE_HIERARCHY.get(current_user.role, 0)
        if user_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Minimum required role: {min_role}",
            )
        return current_user
    return role_checker


# Shorthand dependencies
require_admin = require_roles("admin")
require_hr_manager = require_roles("admin", "hr_manager")
require_hr_analyst = require_roles("admin", "hr_manager", "hr_analyst")
require_any_authenticated = get_current_active_user
