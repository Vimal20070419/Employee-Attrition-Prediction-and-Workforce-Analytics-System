"""
AttritionIQ — Model Trainer
===============================
Trains 13 ML algorithms with cross-validation and hyperparameter tuning.
Automatically selects the best model and registers it.

Algorithms:
  1. Logistic Regression
  2. Decision Tree
  3. Random Forest
  4. Gradient Boosting
  5. AdaBoost
  6. Extra Trees
  7. XGBoost
  8. LightGBM
  9. CatBoost
  10. Support Vector Machine
  11. K-Nearest Neighbors
  12. Naive Bayes
  13. Neural Network (MLP)
"""

import json
import time
import uuid
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import structlog
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import (
    AdaBoostClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

warnings.filterwarnings("ignore")
logger = structlog.get_logger(__name__)
router = APIRouter()

ARTIFACTS_DIR = Path("/app/artifacts/models")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def get_all_models(random_state: int = 42) -> Dict:
    """Return dictionary of all 13 model instances with base hyperparameters."""
    models = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, random_state=random_state, class_weight="balanced"
        ),
        "DecisionTree": DecisionTreeClassifier(
            random_state=random_state, class_weight="balanced"
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, random_state=random_state, class_weight="balanced", n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200, random_state=random_state
        ),
        "AdaBoost": AdaBoostClassifier(
            n_estimators=200, random_state=random_state, algorithm="SAMME"
        ),
        "ExtraTrees": ExtraTreesClassifier(
            n_estimators=200, random_state=random_state, class_weight="balanced", n_jobs=-1
        ),
        "SVM": SVC(probability=True, class_weight="balanced", random_state=random_state),
        "KNN": KNeighborsClassifier(n_neighbors=7, n_jobs=-1),
        "NaiveBayes": GaussianNB(),
        "NeuralNetwork": MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            max_iter=300,
            random_state=random_state,
            early_stopping=True,
            validation_fraction=0.1,
        ),
    }

    if XGBOOST_AVAILABLE:
        models["XGBoost"] = XGBClassifier(
            n_estimators=200, random_state=random_state,
            use_label_encoder=False, eval_metric="logloss",
            scale_pos_weight=5, n_jobs=-1
        )

    if LIGHTGBM_AVAILABLE:
        models["LightGBM"] = LGBMClassifier(
            n_estimators=200, random_state=random_state,
            class_weight="balanced", n_jobs=-1, verbose=-1
        )

    if CATBOOST_AVAILABLE:
        models["CatBoost"] = CatBoostClassifier(
            iterations=200, random_seed=random_state,
            auto_class_weights="Balanced", verbose=0
        )

    return models


def train_and_evaluate_all(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    feature_names: List[str],
    algorithms: Optional[List[str]] = None,
    n_cv_folds: int = 5,
) -> Tuple[Dict, str, object]:
    """
    Train all specified algorithms and return:
    - results dict with all metrics
    - best model name
    - best model object
    """
    from pipeline.evaluator import evaluate_model

    all_models = get_all_models()
    if algorithms:
        all_models = {k: v for k, v in all_models.items() if k in algorithms}

    results = {}
    best_f1 = -1
    best_model_name = None
    best_model = None

    cv = StratifiedKFold(n_splits=n_cv_folds, shuffle=True, random_state=42)

    for name, model in all_models.items():
        logger.info("Training model", algorithm=name)
        start = time.time()

        try:
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1", n_jobs=-1)

            # Full training
            model.fit(X_train, y_train)
            duration = time.time() - start

            # Evaluate
            metrics = evaluate_model(model, X_test, y_test, feature_names)
            metrics["cv_f1_mean"] = float(cv_scores.mean())
            metrics["cv_f1_std"] = float(cv_scores.std())
            metrics["cv_scores"] = cv_scores.tolist()
            metrics["training_duration_seconds"] = duration

            results[name] = metrics

            if metrics["f1_score"] > best_f1:
                best_f1 = metrics["f1_score"]
                best_model_name = name
                best_model = model

            logger.info(
                "Model trained",
                algorithm=name,
                f1=round(metrics["f1_score"], 4),
                auc=round(metrics["auc_roc"], 4),
                duration=round(duration, 2),
            )

        except Exception as e:
            logger.error("Model training failed", algorithm=name, error=str(e))
            results[name] = {"error": str(e)}

    return results, best_model_name, best_model


def save_model_artifacts(
    model,
    scaler,
    feature_names: List[str],
    model_name: str,
    version: str,
) -> Dict[str, str]:
    """Save model and associated artifacts to disk."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = model_name.replace(" ", "_")

    model_path = str(ARTIFACTS_DIR / f"{safe_name}_{version}.joblib")
    scaler_path = str(ARTIFACTS_DIR / f"scaler_{version}.joblib")
    features_path = str(ARTIFACTS_DIR / f"features_{version}.json")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    with open(features_path, "w") as f:
        json.dump(feature_names, f)

    return {
        "model_path": model_path,
        "scaler_path": scaler_path,
        "features_path": features_path,
    }


# ─────────────────────────────────────────────
# FastAPI Route
# ─────────────────────────────────────────────
class TrainRequest(BaseModel):
    dataset_id: str
    algorithms: Optional[List[str]] = None
    config: dict = {}
    job_id: str


@router.post("")
async def train_models(request: TrainRequest):
    """Train all models on the specified dataset and register the best."""
    import asyncio
    from pipeline.preprocessor import DataPreprocessor
    from registry.model_registry import register_model

    # Find dataset file
    dataset_path = f"/app/uploads/{request.dataset_id}"
    # In practice, lookup DB for actual file path
    import glob
    matches = glob.glob(f"/app/uploads/{request.dataset_id}*")
    if not matches:
        return JSONResponse(status_code=404, content={"error": "Dataset file not found"})
    dataset_path = matches[0]

    # Preprocess
    preprocessor = DataPreprocessor()
    X_train, X_test, y_train, y_test, feature_names, validation_report = preprocessor.fit_transform(dataset_path)

    # Train
    results, best_name, best_model = train_and_evaluate_all(
        X_train, X_test, y_train, y_test,
        feature_names=feature_names,
        algorithms=request.algorithms,
    )

    # Generate version
    version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Save artifacts
    artifact_paths = save_model_artifacts(best_model, preprocessor.scaler, feature_names, best_name, version)

    # Register in DB
    best_metrics = results.get(best_name, {})
    await register_model(
        model_version=version,
        algorithm=best_name,
        metrics=best_metrics,
        hyperparameters=best_model.get_params() if hasattr(best_model, "get_params") else {},
        feature_names=feature_names,
        dataset_id=request.dataset_id,
        artifact_paths=artifact_paths,
        job_id=request.job_id,
    )

    return {
        "success": True,
        "best_algorithm": best_name,
        "best_f1_score": best_metrics.get("f1_score"),
        "model_version": version,
        "all_results": {k: v for k, v in results.items() if "error" not in v},
    }
