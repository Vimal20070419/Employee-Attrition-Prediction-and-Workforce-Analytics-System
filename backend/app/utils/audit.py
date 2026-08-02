"""AttritionIQ — Audit Log Utility"""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import AuditLog


async def log_audit(
    db: AsyncSession,
    user_id: Optional[uuid.UUID],
    action: str,
    resource_type: str = None,
    resource_id: str = None,
    description: str = None,
    ip_address: str = None,
    metadata: dict = None,
) -> None:
    """Write an audit log entry."""
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        ip_address=ip_address,
        audit_metadata=metadata or {},
    )
    db.add(log)
    # Do not commit — caller commits
