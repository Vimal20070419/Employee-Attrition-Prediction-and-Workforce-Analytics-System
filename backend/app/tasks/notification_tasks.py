"""AttritionIQ — Notification Tasks + Audit Utility"""

import asyncio
import uuid
from datetime import datetime, timezone

import structlog
from app.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.tasks.notification_tasks.push_notification", queue="notifications")
def push_notification(
    user_id: str,
    type: str,
    title: str,
    message: str,
    data: dict = None,
) -> dict:
    """Push in-app notification to a user's preferences storage."""

    async def _push():
        from app.database import AsyncSessionLocal
        from app.models.user import User
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            if user_id == "all_hr":
                result = await db.execute(
                    select(User).where(User.role.in_(["admin", "hr_manager", "hr_analyst"]))
                )
                users = result.scalars().all()
            else:
                result = await db.execute(select(User).where(User.id == user_id))
                users = [result.scalar_one_or_none()]

            notification = {
                "id": str(uuid.uuid4()),
                "type": type,
                "title": title,
                "message": message,
                "data": data or {},
                "read": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            for user in users:
                if not user:
                    continue
                prefs = dict(user.preferences or {})
                notifications = prefs.get("notifications", [])
                notifications.insert(0, notification)
                prefs["notifications"] = notifications[:100]  # keep last 100
                user.preferences = prefs

            await db.commit()

    asyncio.run(_push())
    return {"success": True}


@celery_app.task(name="app.tasks.notification_tasks.cleanup_old_notifications", queue="notifications")
def cleanup_old_notifications(older_than_days: int = 30) -> dict:
    """Remove notifications older than N days from all users."""
    from datetime import timedelta

    async def _cleanup():
        from app.database import AsyncSessionLocal
        from app.models.user import User
        from sqlalchemy import select

        cutoff = (datetime.now(timezone.utc) - timedelta(days=older_than_days)).isoformat()
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.is_active == True))
            users = result.scalars().all()
            for user in users:
                prefs = dict(user.preferences or {})
                notifications = prefs.get("notifications", [])
                prefs["notifications"] = [n for n in notifications if n.get("created_at", "") > cutoff]
                user.preferences = prefs
            await db.commit()

    asyncio.run(_cleanup())
    return {"success": True, "cleaned_older_than_days": older_than_days}
