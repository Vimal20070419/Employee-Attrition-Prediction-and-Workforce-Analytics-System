"""AttritionIQ — Model Registry Schemas"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class ModelRegistryBase(BaseModel):
    model_version: str
    algorithm: str
    accuracy: Optional[float] = None
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    auc_pr: Optional[float] = None
    log_loss: Optional[float] = None
    training_duration_seconds: Optional[float] = None
    hyperparameters: Optional[Dict] = None
    feature_names: Optional[List[str]] = None
    cv_scores: Optional[Dict] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class ModelRegistryCreate(ModelRegistryBase):
    model_path: str
    scaler_path: Optional[str] = None
    dataset_id: Optional[uuid.UUID] = None


class ModelRegistryResponse(ModelRegistryBase):
    id: uuid.UUID
    status: str
    model_path: str
    scaler_path: Optional[str]
    training_date: datetime
    promoted_at: Optional[datetime]
    archived_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ModelComparisonItem(BaseModel):
    id: uuid.UUID
    model_version: str
    algorithm: str
    status: str
    accuracy: Optional[float]
    precision_score: Optional[float]
    recall_score: Optional[float]
    f1_score: Optional[float]
    auc_roc: Optional[float]
    training_date: Optional[datetime]
