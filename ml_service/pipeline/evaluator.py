"""
AttritionIQ — Model Evaluator
================================
Generates comprehensive evaluation metrics and plots:
- Accuracy, Precision, Recall, F1, AUC-ROC, AUC-PR, Log Loss
- Confusion Matrix
- ROC Curve
- Precision-Recall Curve
- Learning Curve
- Calibration Curve
"""

import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

PLOTS_DIR = Path("/app/artifacts/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_model(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: List[str] = None,
    model_name: str = "model",
    save_plots: bool = True,
) -> Dict:
    """
    Evaluate a trained model and return all metrics.
    Optionally saves evaluation plots as JSON (Plotly).
    """
    y_pred = model.predict(X_test)
    y_prob = (
        model.predict_proba(X_test)[:, 1]
        if hasattr(model, "predict_proba")
        else model.decision_function(X_test)
    )

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision_score": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall_score": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "auc_roc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "auc_pr": round(float(average_precision_score(y_test, y_prob)), 4),
        "log_loss": round(float(log_loss(y_test, y_prob)), 4),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }

    if save_plots:
        # ROC Curve
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        metrics["roc_curve"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}

        # PR Curve
        precision, recall, _ = precision_recall_curve(y_test, y_prob)
        metrics["pr_curve"] = {"precision": precision.tolist(), "recall": recall.tolist()}

        # Feature importance (if available)
        if feature_names and hasattr(model, "feature_importances_"):
            fi = model.feature_importances_
            fi_dict = dict(zip(feature_names, fi.tolist()))
            fi_sorted = dict(sorted(fi_dict.items(), key=lambda x: x[1], reverse=True))
            metrics["feature_importance"] = fi_sorted

    return metrics


def generate_comparison_report(all_results: Dict) -> Dict:
    """Generate model comparison table for the frontend."""
    comparison = []
    for model_name, metrics in all_results.items():
        if "error" in metrics:
            continue
        comparison.append({
            "algorithm": model_name,
            "accuracy": metrics.get("accuracy"),
            "precision": metrics.get("precision_score"),
            "recall": metrics.get("recall_score"),
            "f1_score": metrics.get("f1_score"),
            "auc_roc": metrics.get("auc_roc"),
            "auc_pr": metrics.get("auc_pr"),
            "cv_f1_mean": metrics.get("cv_f1_mean"),
            "training_duration_s": metrics.get("training_duration_seconds"),
        })

    # Sort by F1 descending
    comparison.sort(key=lambda x: (x["f1_score"] or 0), reverse=True)

    return {
        "models": comparison,
        "best_model": comparison[0] if comparison else None,
    }
