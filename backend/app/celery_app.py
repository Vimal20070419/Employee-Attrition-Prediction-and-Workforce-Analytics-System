"""
AttritionIQ — Celery Application
====================================
Celery instance configuration with Redis broker and result backend.
Supports queues: training, reports, shap, notifications.
"""

from celery import Celery
from celery.utils.log import get_task_logger

from app.config import settings

logger = get_task_logger(__name__)


def create_celery_app() -> Celery:
    """Create and configure the Celery application."""

    celery_app = Celery(
        "attritioniq",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=[
            "app.tasks.training_tasks",
            "app.tasks.report_tasks",
            "app.tasks.shap_tasks",
            "app.tasks.notification_tasks",
        ],
    )

    # ========================
    # Celery Configuration
    # ========================
    celery_app.conf.update(
        # Serialization
        task_serializer=settings.CELERY_TASK_SERIALIZER,
        result_serializer=settings.CELERY_RESULT_SERIALIZER,
        accept_content=["json"],

        # Timezone
        timezone=settings.CELERY_TIMEZONE,
        enable_utc=True,

        # Result expiry
        result_expires=86400,  # 24 hours

        # Task routing — dedicated queues per task type
        task_routes={
            "app.tasks.training_tasks.*": {"queue": "training"},
            "app.tasks.report_tasks.*": {"queue": "reports"},
            "app.tasks.shap_tasks.*": {"queue": "shap"},
            "app.tasks.notification_tasks.*": {"queue": "notifications"},
        },

        # Queue definitions
        task_queues={
            "training": {"exchange": "training", "routing_key": "training"},
            "reports": {"exchange": "reports", "routing_key": "reports"},
            "shap": {"exchange": "shap", "routing_key": "shap"},
            "notifications": {"exchange": "notifications", "routing_key": "notifications"},
        },

        # Retry configuration
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        task_max_retries=3,

        # Concurrency
        worker_prefetch_multiplier=1,  # fair distribution for long ML tasks
        task_soft_time_limit=3600,     # 1 hour soft limit
        task_time_limit=7200,          # 2 hour hard limit

        # Monitoring
        worker_send_task_events=True,
        task_send_sent_event=True,

        # Beat schedule imported separately
        beat_schedule_filename="/tmp/celerybeat-schedule",
    )

    return celery_app


celery_app = create_celery_app()
