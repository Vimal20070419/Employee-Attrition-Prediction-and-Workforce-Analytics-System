"""
AttritionIQ — Celery SHAP Tasks
==================================
Background SHAP analysis for individual and batch employees.
"""

import asyncio
import uuid
from datetime import datetime, timezone

import httpx
import structlog

from app.celery_app import celery_app
from app.config import settings

logger = structlog.get_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.shap_tasks.run_shap_analysis",
    max_retries=3,
    queue="shap",
    soft_time_limit=1800,
)
def run_shap_analysis(self, employee_id: str, model_version: str = None) -> dict:
    """Compute SHAP values for a single employee asynchronously."""
    logger.info("SHAP analysis started", employee_id=employee_id)
    try:
        response = httpx.post(
            f"{settings.ML_SERVICE_URL}/shap/explain",
            json={"employee_id": employee_id, "model_version": model_version},
            timeout=300,
        )
        response.raise_for_status()
        result = response.json()
        logger.info("SHAP analysis complete", employee_id=employee_id)
        return result
    except Exception as exc:
        logger.error("SHAP analysis failed", employee_id=employee_id, error=str(exc))
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(
    bind=True,
    name="app.tasks.shap_tasks.run_batch_shap_analysis",
    max_retries=2,
    queue="shap",
    soft_time_limit=3600,
)
def run_batch_shap_analysis(
    self,
    employee_ids: list = None,
    threshold: float = 0.70,
) -> dict:
    """
    Batch SHAP analysis — run for all high-risk employees
    or a specific list. Triggered daily by Celery Beat.
    """
    logger.info("Batch SHAP analysis started", count=len(employee_ids or []))

    if not employee_ids:
        # Fetch high-risk employees from DB
        employee_ids = asyncio.run(get_high_risk_employee_ids(threshold))

    results = []
    batch_id = str(uuid.uuid4())

    for emp_id in employee_ids:
        try:
            response = httpx.post(
                f"{settings.ML_SERVICE_URL}/shap/explain",
                json={"employee_id": emp_id, "batch_id": batch_id},
                timeout=120,
            )
            if response.status_code == 200:
                results.append({"employee_id": emp_id, "status": "success"})
            else:
                results.append({"employee_id": emp_id, "status": "failed"})
        except Exception as e:
            results.append({"employee_id": emp_id, "status": "error", "error": str(e)})

    # Notify on completion
    from app.tasks.notification_tasks import push_notification
    push_notification.apply_async(
        kwargs={
            "user_id": "all_hr",
            "type": "batch_shap_complete",
            "title": "Daily Risk Scan Complete",
            "message": f"Analyzed {len(results)} employees. High-risk employees updated.",
        },
        queue="notifications",
    )

    return {"batch_id": batch_id, "total": len(results), "results": results}


async def get_high_risk_employee_ids(threshold: float) -> list:
    """Fetch IDs of employees with latest prediction probability above threshold."""
    from app.database import AsyncSessionLocal
    from app.models.models import Prediction
    from sqlalchemy import select, desc

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Prediction.employee_id)
            .where(Prediction.attrition_probability >= threshold)
            .order_by(desc(Prediction.created_at))
            .limit(100)
        )
        return [str(row[0]) for row in result.all() if row[0]]
