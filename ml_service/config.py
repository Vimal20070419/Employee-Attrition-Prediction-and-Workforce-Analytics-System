"""AttritionIQ — ML Service Settings"""

import os
from pydantic_settings import BaseSettings


class MLSettings(BaseSettings):
    SERVICE_NAME: str = "AttritionIQ-MLService"
    PORT: int = 8001
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/attrition_db")
    ARTIFACTS_DIR: str = "/app/artifacts"
    MODELS_DIR: str = "/app/artifacts/models"
    SHAP_DIR: str = "/app/artifacts/shap"
    PLOTS_DIR: str = "/app/artifacts/plots"
    REPORTS_DIR: str = "/app/artifacts/reports"
    UPLOADS_DIR: str = "/app/uploads"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


ml_settings = MLSettings()
