"""
AttritionIQ — Analytics Routes
===================================
Dashboard widgets, department analysis, attrition trends,
SHAP feature importance, and EDA data endpoints.
"""

from typing import Optional
import uuid

import structlog
from fastapi import APIRouter, Depends, Query
from fastapi_cache.decorator import cache
from sqlalchemy import func, select, case, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac import require_any_authenticated
from app.database import get_db
from app.models.employee import Employee
from app.models.models import Department, Prediction, ModelRegistry
from app.models.user import User

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/dashboard")
@cache(expire=120)
async def get_dashboard_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Aggregate all dashboard widget data in a single call."""

    # KPIs
    total_employees = await db.scalar(select(func.count(Employee.id)).where(Employee.is_active == True))
    attrition_count = await db.scalar(
        select(func.count(Employee.id)).where(Employee.attrition == "Yes", Employee.is_active == True)
    )
    avg_salary = await db.scalar(select(func.avg(Employee.monthly_income)).where(Employee.is_active == True))
    avg_age = await db.scalar(select(func.avg(Employee.age)).where(Employee.is_active == True))
    avg_years = await db.scalar(select(func.avg(Employee.years_at_company)).where(Employee.is_active == True))
    avg_satisfaction = await db.scalar(select(func.avg(Employee.job_satisfaction)).where(Employee.is_active == True))

    attrition_rate = round((attrition_count / total_employees * 100), 2) if total_employees else 0

    # Department breakdown
    dept_result = await db.execute(
        select(
            Department.name,
            func.count(Employee.id).label("total"),
            func.sum(case((Employee.attrition == "Yes", 1), else_=0)).label("attrited"),
        )
        .join(Employee, Employee.department_id == Department.id)
        .where(Employee.is_active == True)
        .group_by(Department.name)
        .order_by(func.sum(case((Employee.attrition == "Yes", 1), else_=0)).desc())
    )
    departments = [
        {
            "department": row.name,
            "total": row.total,
            "attrited": row.attrited or 0,
            "attrition_rate": round((row.attrited or 0) / row.total * 100, 2) if row.total else 0,
        }
        for row in dept_result.all()
    ]

    # Gender distribution
    gender_result = await db.execute(
        select(Employee.gender, func.count(Employee.id).label("count"))
        .where(Employee.is_active == True)
        .group_by(Employee.gender)
    )
    gender_dist = {row.gender: row.count for row in gender_result.all()}

    # Risk distribution (from predictions)
    risk_result = await db.execute(
        select(Prediction.risk_level, func.count(Prediction.id).label("count"))
        .group_by(Prediction.risk_level)
    )
    risk_dist = {row.risk_level: row.count for row in risk_result.all()}

    # Active model metrics
    model_result = await db.execute(
        select(ModelRegistry).where(ModelRegistry.status == "active")
    )
    active_model = model_result.scalar_one_or_none()
    model_metrics = None
    if active_model:
        model_metrics = {
            "version": active_model.model_version,
            "algorithm": active_model.algorithm,
            "accuracy": active_model.accuracy,
            "f1_score": active_model.f1_score,
            "auc_roc": active_model.auc_roc,
            "training_date": active_model.training_date.isoformat() if active_model.training_date else None,
        }

    # High-risk employees (top 10)
    high_risk_result = await db.execute(
        select(Prediction, Employee)
        .join(Employee, Prediction.employee_id == Employee.id)
        .where(Prediction.attrition_probability >= 0.70)
        .order_by(Prediction.attrition_probability.desc())
        .limit(10)
    )
    high_risk = [
        {
            "employee_id": str(row.Employee.id),
            "job_role": row.Employee.job_role,
            "probability": round(row.Prediction.attrition_probability, 3),
            "risk_level": row.Prediction.risk_level,
            "top_factors": row.Prediction.top_risk_factors[:3],
        }
        for row in high_risk_result.all()
    ]

    return {
        "kpis": {
            "total_employees": total_employees or 0,
            "current_employees": (total_employees - (attrition_count or 0)) if total_employees else 0,
            "employees_left": attrition_count or 0,
            "attrition_rate_pct": attrition_rate,
            "avg_monthly_salary": round(float(avg_salary or 0), 2),
            "avg_age": round(float(avg_age or 0), 1),
            "avg_years_at_company": round(float(avg_years or 0), 1),
            "avg_job_satisfaction": round(float(avg_satisfaction or 0), 2),
        },
        "departments": departments,
        "gender_distribution": gender_dist,
        "risk_distribution": risk_dist,
        "model_performance": model_metrics,
        "high_risk_employees": high_risk,
    }


@router.get("/attrition-trend")
@cache(expire=300)
async def get_attrition_trend(
    months: int = Query(12, ge=3, le=36),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Monthly attrition trend over the past N months."""
    result = await db.execute(
        text("""
            SELECT
                DATE_TRUNC('month', created_at) AS month,
                COUNT(*) AS total,
                SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrited
            FROM employees
            WHERE is_active = TRUE
              AND created_at >= NOW() - INTERVAL ':months months'
            GROUP BY month
            ORDER BY month ASC
        """).bindparams(months=months)
    )
    trend = [
        {
            "month": str(row.month)[:7],
            "total": row.total,
            "attrited": row.attrited or 0,
            "attrition_rate": round((row.attrited or 0) / row.total * 100, 2) if row.total else 0,
        }
        for row in result.all()
    ]
    return {"trend": trend}


@router.get("/department-risk")
@cache(expire=300)
async def get_department_risk_scores(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Department-wise average attrition probability scores."""
    result = await db.execute(
        select(
            Department.name,
            func.avg(Prediction.attrition_probability).label("avg_risk"),
            func.count(Prediction.id).label("prediction_count"),
        )
        .join(Employee, Prediction.employee_id == Employee.id)
        .join(Department, Employee.department_id == Department.id)
        .group_by(Department.name)
        .order_by(func.avg(Prediction.attrition_probability).desc())
    )
    scores = [
        {
            "department": row.name,
            "avg_risk_score": round(float(row.avg_risk or 0), 3),
            "prediction_count": row.prediction_count,
            "risk_category": (
                "Critical" if (row.avg_risk or 0) >= 0.75 else
                "High" if (row.avg_risk or 0) >= 0.55 else
                "Medium" if (row.avg_risk or 0) >= 0.35 else "Low"
            ),
        }
        for row in result.all()
    ]
    return {"department_risk": scores}


@router.get("/shap-importance")
@cache(expire=600)
async def get_global_shap_importance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Fetch global SHAP feature importance from active model."""
    import httpx
    from app.config import settings
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{settings.ML_SERVICE_URL}/shap/global-importance")
            return response.json()
    except Exception:
        return {"features": [], "message": "SHAP data not available yet"}


@router.get("/eda/{dataset_id}")
async def get_eda_results(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Retrieve pre-computed EDA results for a dataset."""
    from app.models.models import UploadedDataset
    result = await db.execute(select(UploadedDataset).where(UploadedDataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset or not dataset.eda_report_path:
        return {"message": "EDA not yet generated for this dataset"}
    import json
    try:
        with open(dataset.eda_report_path) as f:
            eda_data = json.load(f)
        return eda_data
    except Exception:
        return {"message": "EDA report not available"}
