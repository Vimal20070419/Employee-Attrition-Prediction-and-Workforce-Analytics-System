"""
AttritionIQ — Predictions Routes
====================================
Individual prediction, batch prediction, prediction history,
SHAP explanation retrieval, and feedback submission.
"""

import uuid
from typing import List, Optional

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac import require_any_authenticated, require_hr_analyst
from app.config import settings
from app.database import get_db
from app.models.models import Prediction, ModelRegistry
from app.models.user import User
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionListResponse,
    BatchPredictionRequest,
    FeedbackRequest,
)
from app.utils.audit import log_audit

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def predict_attrition(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_analyst),
) -> PredictionResponse:
    """
    Predict attrition for a single employee.
    Calls ML service, stores result with SHAP values.
    """

    # Get active model
    result = await db.execute(
        select(ModelRegistry).where(ModelRegistry.status == "active")
    )
    active_model = result.scalar_one_or_none()
    if not active_model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No active model found. Please train a model first.",
        )

    # Call ML service
    try:
        async with httpx.AsyncClient(timeout=settings.ML_SERVICE_TIMEOUT) as client:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/predict",
                json={
                    "features": request.model_dump(),
                    "model_version": active_model.model_version,
                    "include_shap": True,
                },
            )
            response.raise_for_status()
            ml_result = response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="ML service timeout")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"ML service error: {str(e)}")

    # Determine risk level
    prob = ml_result["attrition_probability"]
    if prob >= 0.85:
        risk_level = "Critical"
    elif prob >= 0.70:
        risk_level = "High"
    elif prob >= 0.50:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Store prediction
    prediction = Prediction(
        employee_id=request.employee_id,
        model_registry_id=active_model.id,
        input_features=request.model_dump(),
        attrition_probability=prob,
        attrition_prediction=ml_result["prediction"],
        risk_level=risk_level,
        shap_values=ml_result.get("shap_values", {}),
        top_risk_factors=ml_result.get("top_risk_factors", []),
        retention_recommendations=ml_result.get("recommendations", []),
        explanation_text=ml_result.get("explanation_text"),
        predicted_by=current_user.id,
    )
    db.add(prediction)
    await db.flush()
    await log_audit(db, current_user.id, "predict", "prediction", str(prediction.id))
    await db.commit()
    await db.refresh(prediction)

    return prediction


@router.post("/batch", status_code=status.HTTP_202_ACCEPTED)
async def batch_predict(
    request: BatchPredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_analyst),
) -> dict:
    """
    Trigger batch prediction via Celery task.
    Returns task_id for polling.
    """
    from app.tasks.shap_tasks import run_batch_shap_analysis
    task = run_batch_shap_analysis.apply_async(
        kwargs={"employee_ids": [str(eid) for eid in request.employee_ids]},
        queue="shap",
    )
    return {"success": True, "task_id": task.id, "message": "Batch prediction started"}


@router.get("", response_model=PredictionListResponse)
async def list_predictions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    employee_id: Optional[uuid.UUID] = None,
    risk_level: Optional[str] = None,
    sort_by: str = Query("created_at"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> PredictionListResponse:
    """List predictions with filtering and pagination."""

    query = select(Prediction).order_by(desc(Prediction.created_at))
    if employee_id:
        query = query.where(Prediction.employee_id == employee_id)
    if risk_level:
        query = query.where(Prediction.risk_level == risk_level)

    total = await db.scalar(select(Prediction).count())
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    predictions = result.scalars().all()

    return PredictionListResponse(
        items=predictions,
        total=total or 0,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size if total else 0,
    )


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> PredictionResponse:
    """Get a specific prediction with full SHAP explanation."""

    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    return prediction


@router.post("/{prediction_id}/feedback")
async def submit_feedback(
    prediction_id: uuid.UUID,
    feedback: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_analyst),
) -> dict:
    """Submit actual attrition outcome for model feedback loop."""

    result = await db.execute(select(Prediction).where(Prediction.id == prediction_id))
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")

    prediction.actual_attrition = feedback.actual_attrition
    prediction.is_verified = True
    from datetime import datetime, timezone
    prediction.feedback_given_at = datetime.now(timezone.utc)
    await db.commit()

    return {"success": True, "message": "Feedback recorded successfully"}


@router.get("/stats/risk-distribution")
async def get_risk_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Get distribution of risk levels across all predictions."""
    from sqlalchemy import func
    result = await db.execute(
        select(Prediction.risk_level, func.count(Prediction.id))
        .group_by(Prediction.risk_level)
    )
    distribution = {row[0]: row[1] for row in result.all()}
    return {"distribution": distribution}
