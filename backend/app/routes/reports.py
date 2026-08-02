"""AttritionIQ — Reports, ModelRegistry, Admin, Notifications Routes (combined)"""

# ─────────────────────────────────────────────
# reports.py
# ─────────────────────────────────────────────
from fastapi import APIRouter as _Router, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import Optional

from app.database import get_db
from app.auth.rbac import require_any_authenticated, require_hr_analyst, require_hr_manager
from app.models.user import User
from app.models.models import Report

router = _Router()


@router.get("")
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """List all generated reports."""
    query = select(Report).where(Report.created_by == current_user.id).order_by(desc(Report.created_at))
    if current_user.role in ("admin", "hr_manager"):
        query = select(Report).order_by(desc(Report.created_at))
    total = await db.scalar(select(func.count(Report.id)))
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    reports = result.scalars().all()
    return {
        "items": [
            {
                "id": str(r.id),
                "title": r.title,
                "report_type": r.report_type,
                "format": r.format,
                "status": r.status,
                "is_scheduled": r.is_scheduled,
                "created_at": r.created_at.isoformat(),
                "download_url": r.download_url,
            }
            for r in reports
        ],
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_report(
    report_type: str,
    format: str,
    dataset_id: Optional[str] = None,
    email_delivery: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_analyst),
) -> dict:
    """Trigger background report generation via Celery."""
    report = Report(
        title=f"{report_type.replace('_', ' ').title()} Report",
        report_type=report_type,
        format=format,
        status="pending",
        email_delivery=email_delivery,
        created_by=current_user.id,
    )
    db.add(report)
    await db.flush()
    from app.tasks.report_tasks import generate_report_task
    task = generate_report_task.apply_async(
        kwargs={
            "report_id": str(report.id),
            "report_type": report_type,
            "format": format,
            "user_email": current_user.email if email_delivery else None,
            "dataset_id": dataset_id,
        },
        queue="reports",
    )
    report.job_id = task.id
    await db.commit()
    return {"success": True, "report_id": str(report.id), "task_id": task.id}


@router.get("/{report_id}/status")
async def get_report_status(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Poll report generation status."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": report.status, "download_url": report.download_url}
