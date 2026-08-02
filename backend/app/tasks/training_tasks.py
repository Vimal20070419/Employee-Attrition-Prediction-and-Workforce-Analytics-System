"""
AttritionIQ — Celery Training Tasks
======================================
Background ML model training pipeline triggered via API.
"""

import time
import uuid
from datetime import datetime, timezone

import httpx
import structlog

from app.celery_app import celery_app
from app.config import settings

logger = structlog.get_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.training_tasks.run_training_task",
    max_retries=2,
    queue="training",
    soft_time_limit=3600,
)
def run_training_task(
    self,
    dataset_id: str,
    user_id: str,
    algorithms: list = None,
    config: dict = None,
) -> dict:
    """
    Run full ML training pipeline in background.

    Steps:
    1. Update training_history status → 'running'
    2. Call ML service /train endpoint
    3. ML service: preprocess → EDA → feature eng → train 13 models → evaluate → register best
    4. Update training_history → 'completed'
    5. Fire notification to user
    """
    import asyncio
    from app.database import AsyncSessionLocal
    from app.models.models import TrainingHistory, ModelRegistry

    job_id = self.request.id
    logger.info("Training task started", job_id=job_id, dataset_id=dataset_id)

    # Update training history
    async def update_status(status: str, **kwargs):
        async with AsyncSessionLocal() as db:
            from sqlalchemy import update
            await db.execute(
                update(TrainingHistory)
                .where(TrainingHistory.job_id == job_id)
                .values(status=status, **kwargs)
            )
            await db.commit()

    try:
        # Create training history record
        async def create_history():
            async with AsyncSessionLocal() as db:
                history = TrainingHistory(
                    job_id=job_id,
                    dataset_id=uuid.UUID(dataset_id),
                    status="running",
                    started_at=datetime.now(timezone.utc),
                    triggered_by=uuid.UUID(user_id),
                    algorithms_trained=algorithms or [],
                    training_config=config or {},
                )
                db.add(history)
                await db.commit()

        asyncio.run(create_history())

        # Call ML service
        start_time = time.time()
        response = httpx.post(
            f"{settings.ML_SERVICE_URL}/train",
            json={
                "dataset_id": dataset_id,
                "algorithms": algorithms,
                "config": config or {},
                "job_id": job_id,
            },
            timeout=settings.ML_SERVICE_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()

        duration = time.time() - start_time

        # Mark completed
        asyncio.run(update_status(
            "completed",
            completed_at=datetime.now(timezone.utc),
            duration_seconds=duration,
            best_algorithm=result.get("best_algorithm"),
            best_f1_score=result.get("best_f1_score"),
            all_results=result.get("all_results", {}),
        ))

        # Send notification
        send_training_notification.apply_async(
            kwargs={
                "user_id": user_id,
                "status": "completed",
                "best_algorithm": result.get("best_algorithm"),
                "f1_score": result.get("best_f1_score"),
            },
            queue="notifications",
        )

        logger.info("Training completed", job_id=job_id, best=result.get("best_algorithm"))
        return result

    except Exception as exc:
        logger.error("Training failed", job_id=job_id, error=str(exc))
        asyncio.run(update_status("failed", error_message=str(exc), completed_at=datetime.now(timezone.utc)))
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="app.tasks.training_tasks.check_and_trigger_retraining", queue="training")
def check_and_trigger_retraining(f1_threshold: float = 0.80) -> dict:
    """
    Scheduled task: check if active model F1 score has degraded.
    If below threshold, trigger retraining on latest dataset.
    """
    import asyncio
    from app.database import AsyncSessionLocal
    from app.models.models import ModelRegistry, UploadedDataset
    from sqlalchemy import select, desc

    async def check():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ModelRegistry).where(ModelRegistry.status == "active"))
            model = result.scalar_one_or_none()
            if not model or (model.f1_score or 1.0) >= f1_threshold:
                return {"triggered": False, "reason": "Model performance is acceptable"}

            dataset_result = await db.execute(
                select(UploadedDataset).where(UploadedDataset.is_validated == True)
                .order_by(desc(UploadedDataset.created_at)).limit(1)
            )
            dataset = dataset_result.scalar_one_or_none()
            if not dataset:
                return {"triggered": False, "reason": "No validated dataset available"}

            task = run_training_task.apply_async(
                kwargs={"dataset_id": str(dataset.id), "user_id": "system", "algorithms": None},
                queue="training",
            )
            return {"triggered": True, "task_id": task.id, "reason": f"F1 below threshold {f1_threshold}"}

    return asyncio.run(check())


@celery_app.task(name="app.tasks.training_tasks.send_training_notification", queue="notifications")
def send_training_notification(user_id: str, status: str, **kwargs) -> None:
    """Send in-app notification for training completion."""
    from app.tasks.notification_tasks import push_notification
    push_notification.apply_async(
        kwargs={
            "user_id": user_id,
            "type": "training_complete",
            "title": f"Model Training {status.capitalize()}",
            "message": f"Best model: {kwargs.get('best_algorithm', 'N/A')} — F1: {kwargs.get('f1_score', 'N/A')}",
        },
        queue="notifications",
    )
