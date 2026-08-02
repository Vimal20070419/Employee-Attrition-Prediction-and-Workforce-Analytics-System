"""AttritionIQ — Model Registry Routes"""

import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac import require_any_authenticated, require_hr_analyst, require_hr_manager
from app.database import get_db
from app.models.models import ModelRegistry
from app.models.user import User

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("")
async def list_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """List all registered models sorted by training date."""
    query = select(ModelRegistry).order_by(desc(ModelRegistry.training_date))
    if status_filter:
        query = query.where(ModelRegistry.status == status_filter)
    total = await db.scalar(select(func.count(ModelRegistry.id)))
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    models = result.scalars().all()
    return {
        "items": [
            {
                "id": str(m.id),
                "model_version": m.model_version,
                "algorithm": m.algorithm,
                "accuracy": m.accuracy,
                "f1_score": m.f1_score,
                "auc_roc": m.auc_roc,
                "status": m.status,
                "training_date": m.training_date.isoformat() if m.training_date else None,
            }
            for m in models
        ],
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }


@router.get("/active")
async def get_active_model(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Get the currently active (champion) model."""
    result = await db.execute(select(ModelRegistry).where(ModelRegistry.status == "active"))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="No active model found")
    return {
        "id": str(model.id),
        "model_version": model.model_version,
        "algorithm": model.algorithm,
        "accuracy": model.accuracy,
        "precision_score": model.precision_score,
        "recall_score": model.recall_score,
        "f1_score": model.f1_score,
        "auc_roc": model.auc_roc,
        "auc_pr": model.auc_pr,
        "hyperparameters": model.hyperparameters,
        "feature_names": model.feature_names,
        "cv_scores": model.cv_scores,
        "training_date": model.training_date.isoformat() if model.training_date else None,
        "promoted_at": model.promoted_at.isoformat() if model.promoted_at else None,
        "notes": model.notes,
    }


@router.get("/{model_id}")
async def get_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Get full model details."""
    result = await db.execute(select(ModelRegistry).where(ModelRegistry.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return {
        "id": str(model.id),
        "model_version": model.model_version,
        "algorithm": model.algorithm,
        "status": model.status,
        "accuracy": model.accuracy,
        "precision_score": model.precision_score,
        "recall_score": model.recall_score,
        "f1_score": model.f1_score,
        "auc_roc": model.auc_roc,
        "auc_pr": model.auc_pr,
        "log_loss": model.log_loss,
        "training_duration_seconds": model.training_duration_seconds,
        "hyperparameters": model.hyperparameters,
        "feature_names": model.feature_names,
        "cv_scores": model.cv_scores,
        "training_config": model.training_config,
        "model_path": model.model_path,
        "shap_values_path": model.shap_values_path,
        "training_date": model.training_date.isoformat() if model.training_date else None,
        "promoted_at": model.promoted_at.isoformat() if model.promoted_at else None,
        "archived_at": model.archived_at.isoformat() if model.archived_at else None,
        "notes": model.notes,
        "tags": model.tags,
    }


@router.post("/{model_id}/promote", status_code=status.HTTP_200_OK)
async def promote_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_manager),
) -> dict:
    """Promote a model to active status (archives the current active model)."""
    result = await db.execute(select(ModelRegistry).where(ModelRegistry.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    if model.status == "active":
        return {"message": "Model is already active"}

    # Archive current active model
    await db.execute(
        update(ModelRegistry)
        .where(ModelRegistry.status == "active")
        .values(status="archived", archived_at=datetime.now(timezone.utc))
    )

    # Promote this model
    await db.execute(
        update(ModelRegistry)
        .where(ModelRegistry.id == model_id)
        .values(status="active", promoted_at=datetime.now(timezone.utc))
    )
    await db.commit()
    logger.info("Model promoted", model_id=str(model_id), by=str(current_user.id))
    return {"success": True, "message": f"Model {model.model_version} promoted to active"}


@router.post("/{model_id}/archive")
async def archive_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_manager),
) -> dict:
    """Archive a model."""
    result = await db.execute(select(ModelRegistry).where(ModelRegistry.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    if model.status == "active":
        raise HTTPException(status_code=400, detail="Cannot archive the active model. Promote another first.")
    await db.execute(
        update(ModelRegistry)
        .where(ModelRegistry.id == model_id)
        .values(status="archived", archived_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return {"success": True, "message": "Model archived"}


@router.get("/compare/all")
async def compare_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Return metrics table for all models for comparison."""
    result = await db.execute(select(ModelRegistry).order_by(desc(ModelRegistry.f1_score)))
    models = result.scalars().all()
    return {
        "models": [
            {
                "id": str(m.id),
                "version": m.model_version,
                "algorithm": m.algorithm,
                "status": m.status,
                "accuracy": m.accuracy,
                "f1_score": m.f1_score,
                "auc_roc": m.auc_roc,
                "precision": m.precision_score,
                "recall": m.recall_score,
                "training_date": m.training_date.isoformat() if m.training_date else None,
            }
            for m in models
        ]
    }
