"""
AttritionIQ — Model Registry (ML Service Side)
================================================
Registers trained models into PostgreSQL via SQLAlchemy.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

logger = structlog.get_logger(__name__)

import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
ASYNC_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("postgres://", "postgresql+asyncpg://")

engine = create_async_engine(ASYNC_URL, pool_pre_ping=True)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def register_model(
    model_version: str,
    algorithm: str,
    metrics: Dict,
    hyperparameters: Dict,
    feature_names: List[str],
    dataset_id: str,
    artifact_paths: Dict,
    job_id: str,
    notes: str = None,
) -> str:
    """
    Insert a new model version into model_registry table.
    Promotes this model to 'active' and archives the previous active.
    Returns the new model ID.
    """
    model_id = str(uuid.uuid4())

    async with Session() as db:
        # Archive existing active model
        await db.execute(
            text("""
                UPDATE model_registry
                SET status = 'archived', archived_at = NOW()
                WHERE status = 'active'
            """)
        )

        # Insert new active model
        await db.execute(
            text("""
                INSERT INTO model_registry (
                    id, model_version, algorithm,
                    accuracy, precision_score, recall_score, f1_score,
                    auc_roc, auc_pr, log_loss, training_duration_seconds,
                    hyperparameters, feature_names,
                    model_path, scaler_path, shap_values_path,
                    status, dataset_id, notes,
                    training_date, promoted_at, created_at, updated_at
                ) VALUES (
                    :id, :version, :algorithm,
                    :accuracy, :precision, :recall, :f1,
                    :auc_roc, :auc_pr, :log_loss, :duration,
                    :hyperparams, :features,
                    :model_path, :scaler_path, :shap_path,
                    'active', :dataset_id, :notes,
                    NOW(), NOW(), NOW(), NOW()
                )
            """),
            {
                "id": model_id,
                "version": model_version,
                "algorithm": algorithm,
                "accuracy": metrics.get("accuracy"),
                "precision": metrics.get("precision_score"),
                "recall": metrics.get("recall_score"),
                "f1": metrics.get("f1_score"),
                "auc_roc": metrics.get("auc_roc"),
                "auc_pr": metrics.get("auc_pr"),
                "log_loss": metrics.get("log_loss"),
                "duration": metrics.get("training_duration_seconds"),
                "hyperparams": str(hyperparameters),
                "features": str(feature_names),
                "model_path": artifact_paths.get("model_path"),
                "scaler_path": artifact_paths.get("scaler_path"),
                "shap_path": None,
                "dataset_id": dataset_id,
                "notes": notes,
            },
        )
        await db.commit()

    logger.info("Model registered", model_id=model_id, version=model_version, algorithm=algorithm)
    return model_id
