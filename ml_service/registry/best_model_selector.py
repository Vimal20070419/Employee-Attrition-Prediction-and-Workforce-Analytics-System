"""AttritionIQ — Best Model Selector Module"""

from typing import Dict, Tuple


class BestModelSelector:
    """Selects champion model based on weighted score (F1, AUC-ROC, Accuracy)."""

    @staticmethod
    def select_best(results: Dict[str, Dict], primary_metric: str = "f1_score") -> Tuple[str, Dict]:
        best_name = None
        best_score = -1.0
        best_metrics = {}

        for name, metrics in results.items():
            if "error" in metrics:
                continue
            # Composite score: 60% F1, 30% AUC-ROC, 10% Accuracy
            score = (
                0.60 * metrics.get("f1_score", 0) +
                0.30 * metrics.get("auc_roc", 0) +
                0.10 * metrics.get("accuracy", 0)
            )
            if score > best_score:
                best_score = score
                best_name = name
                best_metrics = metrics

        return best_name, best_metrics
