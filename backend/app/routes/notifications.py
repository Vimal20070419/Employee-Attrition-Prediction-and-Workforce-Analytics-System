"""AttritionIQ — Notifications Routes"""

import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac import require_any_authenticated
from app.database import get_db
from app.models.user import User

router = APIRouter()

# In-memory notification store (replace with DB table in production)
# For now, notifications are stored as JSON in user.preferences["notifications"]

@router.get("")
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    unread_only: bool = Query(False),
    current_user: User = Depends(require_any_authenticated),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get notifications for current user."""
    notifications = current_user.preferences.get("notifications", [])
    if unread_only:
        notifications = [n for n in notifications if not n.get("read", False)]
    total = len(notifications)
    start = (page - 1) * page_size
    return {
        "items": notifications[start: start + page_size],
        "total": total,
        "unread_count": sum(1 for n in current_user.preferences.get("notifications", []) if not n.get("read")),
        "page": page,
        "page_size": page_size,
    }


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(require_any_authenticated),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Mark a notification as read."""
    notifications = current_user.preferences.get("notifications", [])
    for n in notifications:
        if n.get("id") == notification_id:
            n["read"] = True
    prefs = dict(current_user.preferences)
    prefs["notifications"] = notifications
    current_user.preferences = prefs
    await db.commit()
    return {"success": True}


@router.post("/read-all")
async def mark_all_read(
    current_user: User = Depends(require_any_authenticated),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Mark all notifications as read."""
    notifications = current_user.preferences.get("notifications", [])
    for n in notifications:
        n["read"] = True
    prefs = dict(current_user.preferences)
    prefs["notifications"] = notifications
    current_user.preferences = prefs
    await db.commit()
    return {"success": True, "message": "All notifications marked as read"}


@router.delete("")
async def clear_notifications(
    current_user: User = Depends(require_any_authenticated),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Clear all notifications."""
    prefs = dict(current_user.preferences)
    prefs["notifications"] = []
    current_user.preferences = prefs
    await db.commit()
    return {"success": True, "message": "All notifications cleared"}
