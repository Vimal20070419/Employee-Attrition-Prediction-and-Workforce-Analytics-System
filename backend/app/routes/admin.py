"""AttritionIQ — Admin Routes"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac import require_admin
from app.database import get_db
from app.models.user import User
from app.models.models import AuditLog

router = APIRouter()


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Admin: list all users."""
    total = await db.scalar(select(func.count(User.id)))
    result = await db.execute(
        select(User).order_by(desc(User.created_at)).offset((page - 1) * page_size).limit(page_size)
    )
    users = result.scalars().all()
    return {
        "items": [
            {
                "id": str(u.id),
                "email": u.email,
                "username": u.username,
                "full_name": u.full_name,
                "role": u.role,
                "status": u.status,
                "is_verified": u.is_verified,
                "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
        "total": total or 0,
    }


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: uuid.UUID,
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Admin: update user role."""
    allowed_roles = ["admin", "hr_manager", "hr_analyst", "viewer"]
    if role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {allowed_roles}")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    await db.commit()
    return {"success": True, "message": f"Role updated to {role}"}


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: uuid.UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Admin: activate/suspend a user."""
    allowed_statuses = ["active", "inactive", "suspended"]
    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = status
    await db.commit()
    return {"success": True, "message": f"User status updated to {status}"}


@router.get("/audit-logs")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Admin: view security audit logs."""
    total = await db.scalar(select(func.count(AuditLog.id)))
    result = await db.execute(
        select(AuditLog).order_by(desc(AuditLog.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    )
    logs = result.scalars().all()
    return {
        "items": [
            {
                "id": str(l.id),
                "action": l.action,
                "resource_type": l.resource_type,
                "user_id": str(l.user_id) if l.user_id else None,
                "ip_address": str(l.ip_address) if l.ip_address else None,
                "description": l.description,
                "is_suspicious": l.is_suspicious,
                "created_at": l.created_at.isoformat(),
            }
            for l in logs
        ],
        "total": total or 0,
    }
