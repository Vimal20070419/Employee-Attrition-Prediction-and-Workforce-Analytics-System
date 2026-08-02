"""
AttritionIQ — Celery Beat Periodic Schedule
=============================================
Defines scheduled tasks using Celery Beat crontab expressions.
"""

from celery.schedules import crontab

from app.celery_app import celery_app

celery_app.conf.beat_schedule = {
    # ========================
    # Weekly Attrition Report (Every Monday 8:00 AM)
    # ========================
    "weekly-attrition-report": {
        "task": "app.tasks.report_tasks.generate_scheduled_report",
        "schedule": crontab(day_of_week="monday", hour=8, minute=0),
        "args": [],
        "kwargs": {
            "report_type": "attrition_summary",
            "format": "pdf",
            "email_delivery": True,
        },
        "options": {"queue": "reports"},
    },

    # ========================
    # Daily High-Risk Employee Scan (Every day 7:00 AM)
    # ========================
    "daily-high-risk-scan": {
        "task": "app.tasks.shap_tasks.run_batch_shap_analysis",
        "schedule": crontab(hour=7, minute=0),
        "args": [],
        "kwargs": {"threshold": 0.70},
        "options": {"queue": "shap"},
    },

    # ========================
    # Monthly Model Performance Report (1st of month 9:00 AM)
    # ========================
    "monthly-model-performance-report": {
        "task": "app.tasks.report_tasks.generate_scheduled_report",
        "schedule": crontab(day_of_month=1, hour=9, minute=0),
        "args": [],
        "kwargs": {
            "report_type": "model_performance",
            "format": "excel",
            "email_delivery": True,
        },
        "options": {"queue": "reports"},
    },

    # ========================
    # Notification Cleanup (Every day midnight)
    # ========================
    "daily-notification-cleanup": {
        "task": "app.tasks.notification_tasks.cleanup_old_notifications",
        "schedule": crontab(hour=0, minute=0),
        "args": [],
        "kwargs": {"older_than_days": 30},
        "options": {"queue": "notifications"},
    },

    # ========================
    # Auto Retrain Check (Every Sunday 2:00 AM)
    # Checks if model performance has degraded and triggers retraining
    # ========================
    "weekly-auto-retrain-check": {
        "task": "app.tasks.training_tasks.check_and_trigger_retraining",
        "schedule": crontab(day_of_week="sunday", hour=2, minute=0),
        "args": [],
        "kwargs": {"f1_threshold": 0.80},
        "options": {"queue": "training"},
    },
}
