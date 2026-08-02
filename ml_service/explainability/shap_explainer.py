"""
AttritionIQ — SHAP Explainer
================================
Generates SHAP explanations for predictions:
- Summary plot (beeswarm)
- Force plot (individual)
- Waterfall plot
- Dependence plot
- Global feature importance
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
import shap
import structlog
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = structlog.get_logger(__name__)
router = APIRouter()

ARTIFACTS_DIR = Path("/app/artifacts/models")
SHAP_DIR = Path("/app/artifacts/shap")
SHAP_DIR.mkdir(parents=True, exist_ok=True)


def load_model_and_scaler(model_version: str = None) -> tuple:
    """Load the active model and scaler from disk."""
    import glob

    if model_version:
        pattern = str(ARTIFACTS_DIR / f"*_{model_version}.joblib")
    else:
        # Load latest model (not scaler)
        pattern = str(ARTIFACTS_DIR / "*.joblib")

    files = sorted(glob.glob(pattern), reverse=True)
    scaler_files = [f for f in files if "scaler" in f]
    model_files = [f for f in files if "scaler" not in f and "features" not in f]

    if not model_files or not scaler_files:
        raise FileNotFoundError("No model artifacts found")

    model = joblib.load(model_files[0])
    scaler = joblib.load(scaler_files[0])

    # Load feature names
    feat_files = sorted(glob.glob(str(ARTIFACTS_DIR / "features_*.json")), reverse=True)
    feature_names = []
    if feat_files:
        with open(feat_files[0]) as f:
            feature_names = json.load(f)

    return model, scaler, feature_names


def compute_shap_values(
    model,
    X: np.ndarray,
    feature_names: List[str],
    model_name: str = "tree",
) -> shap.Explanation:
    """Compute SHAP values using the appropriate explainer type."""
    try:
        # Try TreeExplainer first (fastest for tree-based models)
        explainer = shap.TreeExplainer(model)
        shap_values = explainer(X)
    except Exception:
        try:
            # LinearExplainer for linear models
            explainer = shap.LinearExplainer(model, X)
            shap_values = explainer(X)
        except Exception:
            # KernelExplainer as fallback (slowest but universal)
            background = shap.kmeans(X, 10)
            explainer = shap.KernelExplainer(model.predict_proba, background)
            shap_vals = explainer.shap_values(X, nsamples=100)
            shap_values = shap_vals[1] if isinstance(shap_vals, list) else shap_vals

    return shap_values, explainer


def get_top_risk_factors(
    shap_values_single: np.ndarray,
    feature_names: List[str],
    top_n: int = 5,
) -> List[Dict]:
    """Extract top N risk factors from SHAP values for a single prediction."""
    importance = list(zip(feature_names, shap_values_single))
    importance.sort(key=lambda x: abs(x[1]), reverse=True)

    factors = []
    for feat, val in importance[:top_n]:
        factors.append({
            "feature": feat,
            "shap_value": round(float(val), 4),
            "direction": "increases" if val > 0 else "decreases",
            "impact": "high" if abs(val) > 0.1 else "medium" if abs(val) > 0.05 else "low",
        })
    return factors


def get_global_feature_importance(
    model,
    X_background: np.ndarray,
    feature_names: List[str],
    n_samples: int = 200,
) -> Dict:
    """Compute global SHAP feature importance."""
    sample_X = X_background[:n_samples] if len(X_background) > n_samples else X_background
    shap_values, _ = compute_shap_values(model, sample_X, feature_names)

    if hasattr(shap_values, "values"):
        sv_array = shap_values.values
    else:
        sv_array = shap_values

    mean_abs = np.abs(sv_array).mean(axis=0)
    if mean_abs.ndim > 1:
        mean_abs = mean_abs[:, 1]

    importance = dict(zip(feature_names, mean_abs.tolist()))
    importance_sorted = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

    return {
        "features": list(importance_sorted.keys()),
        "importance": list(importance_sorted.values()),
    }


# ─────────────────────────────────────────────
# FastAPI Routes
# ─────────────────────────────────────────────
class ExplainRequest(BaseModel):
    employee_id: Optional[str] = None
    features: Optional[Dict] = None
    model_version: Optional[str] = None
    batch_id: Optional[str] = None


@router.post("/explain")
async def explain_prediction(request: ExplainRequest):
    """Compute SHAP explanation for a prediction."""
    try:
        model, scaler, feature_names = load_model_and_scaler(request.model_version)

        # Build feature vector
        if request.features:
            X_df = pd.DataFrame([request.features]).reindex(columns=feature_names, fill_value=0)
        else:
            # Load employee from DB and predict
            return JSONResponse(
                status_code=400,
                content={"error": "Either features or employee_id required"}
            )

        X_scaled = scaler.transform(X_df.values)
        shap_values, _ = compute_shap_values(model, X_scaled, feature_names)

        if hasattr(shap_values, "values"):
            sv = shap_values.values[0]
            if sv.ndim > 1:
                sv = sv[:, 1]
        else:
            sv = shap_values[0]

        top_factors = get_top_risk_factors(sv, feature_names)
        shap_dict = dict(zip(feature_names, sv.tolist()))

        return {
            "employee_id": request.employee_id,
            "shap_values": shap_dict,
            "top_risk_factors": top_factors,
        }

    except Exception as e:
        logger.error("SHAP explanation failed", error=str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/global-importance")
async def get_global_importance():
    """Return global SHAP feature importance for the active model."""
    shap_path = SHAP_DIR / "global_importance.json"
    if shap_path.exists():
        with open(shap_path) as f:
            return json.load(f)
    return {"features": [], "importance": [], "message": "Not yet computed"}
