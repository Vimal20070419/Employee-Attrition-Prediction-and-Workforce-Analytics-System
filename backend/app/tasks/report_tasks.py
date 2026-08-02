"""
AttritionIQ — Celery Report Tasks
=====================================
Background PDF, Excel, CSV, PowerPoint report generation
with optional email delivery.
"""

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx
import structlog

from app.celery_app import celery_app
from app.config import settings

logger = structlog.get_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.report_tasks.generate_report_task",
    max_retries=2,
    queue="reports",
    soft_time_limit=600,
)
def generate_report_task(
    self,
    report_id: str,
    report_type: str,
    format: str,
    user_email: str = None,
    dataset_id: str = None,
    filters: dict = None,
) -> dict:
    """
    Generate a report in background.

    Steps:
    1. Update report status → 'generating'
    2. Call ML service /reports/generate
    3. Save file, update report record with download URL
    4. If email_delivery: send email with attachment
    5. Push notification to user
    """
    from app.database import AsyncSessionLocal
    from app.models.models import Report
    from sqlalchemy import select, update

    logger.info("Report generation started", report_id=report_id, format=format)

    async def update_report(status: str, **kwargs):
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Report).where(Report.id == report_id).values(status=status, **kwargs)
            )
            await db.commit()

    try:
        asyncio.run(update_report("generating"))

        # Call ML service report generator
        response = httpx.post(
            f"{settings.ML_SERVICE_URL}/reports/generate",
            json={
                "report_type": report_type,
                "format": format,
                "dataset_id": dataset_id,
                "filters": filters or {},
                "report_id": report_id,
            },
            timeout=300,
        )
        response.raise_for_status()
        result = response.json()

        file_path = result.get("file_path")
        download_url = f"/api/v1/reports/{report_id}/download"
        file_size = os.path.getsize(file_path) if file_path and os.path.exists(file_path) else 0

        asyncio.run(update_report(
            "completed",
            file_path=file_path,
            file_size_bytes=file_size,
            download_url=download_url,
            last_run_at=datetime.now(timezone.utc),
        ))

        # Optional email delivery
        if user_email and settings.EMAIL_ENABLED:
            send_report_email.apply_async(
                kwargs={
                    "email": user_email,
                    "report_type": report_type,
                    "file_path": file_path,
                    "format": format,
                },
                queue="notifications",
            )

        logger.info("Report generated", report_id=report_id, file_path=file_path)
        return {"success": True, "download_url": download_url}

    except Exception as exc:
        logger.error("Report generation failed", report_id=report_id, error=str(exc))
        asyncio.run(update_report("failed", error_message=str(exc)))
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(name="app.tasks.report_tasks.generate_scheduled_report", queue="reports")
def generate_scheduled_report(
    report_type: str,
    format: str,
    email_delivery: bool = False,
) -> dict:
    """
    Celery Beat scheduled report generation.
    Creates a report record and delegates to generate_report_task.
    """
    import asyncio
    from app.database import AsyncSessionLocal
    from app.models.models import Report

    async def create_and_trigger():
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            from app.models.user import User
            # Get all admins and hr_managers for email delivery
            result = await db.execute(
                select(User).where(User.role.in_(["admin", "hr_manager"]), User.is_active == True)
            )
            recipients = result.scalars().all()
            recipient_emails = [u.email for u in recipients]

            report = Report(
                title=f"Scheduled {report_type.replace('_', ' ').title()} Report — {datetime.now().strftime('%Y-%m-%d')}",
                report_type=report_type,
                format=format,
                status="pending",
                is_scheduled=True,
                email_delivery=email_delivery,
                recipient_emails=recipient_emails,
                created_by=recipients[0].id if recipients else None,
            )
            db.add(report)
            await db.flush()
            report_id = str(report.id)
            await db.commit()
            return report_id, recipient_emails

    report_id, emails = asyncio.run(create_and_trigger())
    task = generate_report_task.apply_async(
        kwargs={
            "report_id": report_id,
            "report_type": report_type,
            "format": format,
            "user_email": emails[0] if emails and email_delivery else None,
        },
        queue="reports",
    )
    return {"task_id": task.id, "report_id": report_id}


@celery_app.task(name="app.tasks.report_tasks.send_report_email", queue="notifications")
def send_report_email(email: str, report_type: str, file_path: str, format: str) -> None:
    """Send email with report attachment."""
    logger.info("Sending report email", email=email, report_type=report_type)
    # Actual SMTP sending via fastapi-mail would be wired here
