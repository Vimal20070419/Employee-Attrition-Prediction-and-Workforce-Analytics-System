"""
AttritionIQ — Attrition Predictor
=====================================
Loads active model and generates predictions with risk level
and retention recommendations.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
import structlog
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = structlog.get_logger(__name__)
router = APIRouter()

ARTIFACTS_DIR = Path("/app/artifacts/models")


def load_active_model():
    """Load the most recently saved model artifacts."""
    import glob
    model_files = sorted(
        [f for f in glob.glob(str(ARTIFACTS_DIR / "*.joblib")) if "scaler" not in f and "features" not in f],
        reverse=True,
    )
    scaler_files = sorted(glob.glob(str(ARTIFACTS_DIR / "scaler_*.joblib")), reverse=True)
    feat_files = sorted(glob.glob(str(ARTIFACTS_DIR / "features_*.json")), reverse=True)

    if not model_files:
        raise FileNotFoundError("No trained model found")

    model = joblib.load(model_files[0])
    scaler = joblib.load(scaler_files[0]) if scaler_files else None
    feature_names = []
    if feat_files:
        with open(feat_files[0]) as f:
            feature_names = json.load(f)

    return model, scaler, feature_names


def build_recommendation(features: Dict, probability: float, top_factors: List[Dict]) -> List[str]:
    """
    Rule-based + SHAP-guided retention recommendation engine.
    Returns actionable HR recommendations.
    """
    recommendations = []
    factor_names = [f["feature"].lower() for f in top_factors[:5]]

    # Overtime
    if features.get("OverTime") == 1 or "overtime" in str(factor_names):
        recommendations.append({
            "category": "Work-Life Balance",
            "recommendation": "Reduce overtime hours. Consider flexible working arrangements.",
            "priority": "High",
            "action": "Discuss workload distribution with the employee's manager",
        })

    # Low income
    if features.get("MonthlyIncome", 10000) < 5000 or "monthlyincome" in str(factor_names):
        recommendations.append({
            "category": "Compensation",
            "recommendation": "Review and adjust monthly compensation to market rate.",
            "priority": "High",
            "action": "Initiate salary benchmarking review with HR Compensation team",
        })

    # Low job satisfaction
    if features.get("JobSatisfaction", 3) <= 2 or "jobsatisfaction" in str(factor_names):
        recommendations.append({
            "category": "Job Satisfaction",
            "recommendation": "Schedule one-on-one sessions to understand dissatisfiers.",
            "priority": "High",
            "action": "Arrange bi-weekly manager check-ins and satisfaction pulse survey",
        })

    # Low training
    if features.get("TrainingTimesLastYear", 3) <= 1 or "training" in str(factor_names):
        recommendations.append({
            "category": "Learning & Development",
            "recommendation": "Enroll in professional development programs.",
            "priority": "Medium",
            "action": "Identify skill gaps and create a personal development plan",
        })

    # Years since promotion
    if features.get("YearsSinceLastPromotion", 0) >= 3 or "yearssince" in str(factor_names):
        recommendations.append({
            "category": "Career Growth",
            "recommendation": "Create a clear promotion roadmap and timeline.",
            "priority": "Medium",
            "action": "Work with manager on promotion criteria and career ladder",
        })

    # Work-life balance
    if features.get("WorkLifeBalance", 3) <= 2 or "worklifebalance" in str(factor_names):
        recommendations.append({
            "category": "Wellness",
            "recommendation": "Introduce flexible working hours or remote work options.",
            "priority": "Medium",
            "action": "Discuss hybrid work policy with team lead",
        })

    # Environment satisfaction
    if features.get("EnvironmentSatisfaction", 3) <= 2:
        recommendations.append({
            "category": "Workplace Environment",
            "recommendation": "Address workspace concerns and team dynamics.",
            "priority": "Medium",
            "action": "Conduct anonymous environment survey and act on results",
        })

    # Default
    if not recommendations:
        recommendations.append({
            "category": "General Engagement",
            "recommendation": "Conduct regular engagement check-ins.",
            "priority": "Low",
            "action": "Schedule quarterly career development discussions",
        })

    return recommendations


class PredictRequest(BaseModel):
    features: Dict
    model_version: Optional[str] = None
    include_shap: bool = True


@router.post("/predict")
async def predict(request: PredictRequest):
    """Run attrition prediction on provided feature set."""
    try:
        model, scaler, feature_names = load_active_model()

        # Build feature DataFrame
        features = request.features
        X_df = pd.DataFrame([features]).reindex(columns=feature_names, fill_value=0)

        # Encode boolean/string values
        for col in X_df.columns:
            if X_df[col].dtype == object:
                X_df[col] = 1 if str(X_df[col].iloc[0]).lower() in ("yes", "true", "1") else 0

        # Scale
        if scaler:
            X_scaled = scaler.transform(X_df.values)
        else:
            X_scaled = X_df.values

        # Predict
        prob = float(model.predict_proba(X_scaled)[0][1])
        prediction = "Yes" if prob >= 0.5 else "No"

        result = {
            "attrition_probability": round(prob, 4),
            "prediction": prediction,
            "shap_values": {},
            "top_risk_factors": [],
            "recommendations": [],
        }

        # SHAP
        if request.include_shap:
            try:
                from explainability.shap_explainer import compute_shap_values, get_top_risk_factors
                shap_values, _ = compute_shap_values(model, X_scaled, feature_names)
                if hasattr(shap_values, "values"):
                    sv = shap_values.values[0]
                    if sv.ndim > 1:
                        sv = sv[:, 1]
                else:
                    sv = shap_values[0]

                top_factors = get_top_risk_factors(sv, feature_names)
                result["shap_values"] = dict(zip(feature_names, sv.tolist()))
                result["top_risk_factors"] = top_factors
                result["recommendations"] = build_recommendation(features, prob, top_factors)
            except Exception as e:
                logger.warning("SHAP computation failed", error=str(e))

        return result

    except Exception as e:
        logger.error("Prediction failed", error=str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})
