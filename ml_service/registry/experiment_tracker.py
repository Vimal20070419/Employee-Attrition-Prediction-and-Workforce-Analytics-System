"""AttritionIQ — Experiment Tracker Module"""

from typing import Dict, List
import structlog

logger = structlog.get_logger(__name__)


class ExperimentTracker:
    """Logs experiment parameters, hyperparameters, and CV scores during training runs."""

    def __init__(self, experiment_name: str = "attrition_prediction"):
        self.experiment_name = experiment_name
        self.runs: List[Dict] = []

    def log_run(self, algorithm: str, params: Dict, metrics: Dict, cv_scores: List[float]):
        run_data = {
            "algorithm": algorithm,
            "params": params,
            "metrics": metrics,
            "cv_scores": cv_scores,
        }
        self.runs.append(run_data)
        logger.info("Logged experiment run", algorithm=algorithm, f1=metrics.get("f1_score"))

    def get_best_run(self, metric: str = "f1_score") -> Dict:
        if not self.runs:
            return {}
        return max(self.runs, key=lambda r: r["metrics"].get(metric, 0))
