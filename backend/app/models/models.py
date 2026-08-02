"""AttritionIQ — Department, Prediction, Dataset, ModelRegistry, TrainingHistory, AuditLog, Report ORM Models"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, JSON, UUID
)
JSONB = JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


# ============================================================
# Department
# ============================================================
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    manager_name: Mapped[Optional[str]] = mapped_column(String(255))
    headcount: Mapped[int] = mapped_column(Integer, default=0)
    budget: Mapped[Optional[float]] = mapped_column(Float)
    location: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    employees = relationship("Employee", back_populates="department")


# ============================================================
# UploadedDataset
# ============================================================
class UploadedDataset(Base):
    __tablename__ = "uploaded_datasets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_format: Mapped[str] = mapped_column(String(10), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1.0")
    row_count: Mapped[Optional[int]] = mapped_column(Integer)
    column_count: Mapped[Optional[int]] = mapped_column(Integer)
    columns_info: Mapped[dict] = mapped_column(JSONB, default=dict)
    preprocessing_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    validation_report: Mapped[dict] = mapped_column(JSONB, default=dict)
    eda_report_path: Mapped[Optional[str]] = mapped_column(Text)
    checksum: Mapped[Optional[str]] = mapped_column(String(64))
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    uploaded_by_user = relationship("User", back_populates="datasets")
    training_history = relationship("TrainingHistory", back_populates="dataset")
    model_registry = relationship("ModelRegistry", back_populates="dataset")


# ============================================================
# ModelRegistry
# ============================================================
class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    experiment_id: Mapped[Optional[str]] = mapped_column(String(100))
    algorithm: Mapped[str] = mapped_column(String(100), nullable=False)

    # Metrics
    accuracy: Mapped[Optional[float]] = mapped_column(Float)
    precision_score: Mapped[Optional[float]] = mapped_column(Float)
    recall_score: Mapped[Optional[float]] = mapped_column(Float)
    f1_score: Mapped[Optional[float]] = mapped_column(Float)
    auc_roc: Mapped[Optional[float]] = mapped_column(Float)
    auc_pr: Mapped[Optional[float]] = mapped_column(Float)
    log_loss: Mapped[Optional[float]] = mapped_column(Float)
    training_duration_seconds: Mapped[Optional[float]] = mapped_column(Float)

    # Config
    hyperparameters: Mapped[dict] = mapped_column(JSONB, default=dict)
    feature_names: Mapped[list] = mapped_column(JSONB, default=list)
    training_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    cv_scores: Mapped[list] = mapped_column(JSONB, default=list)

    # Artifact paths
    model_path: Mapped[Optional[str]] = mapped_column(Text)
    scaler_path: Mapped[Optional[str]] = mapped_column(Text)
    encoder_path: Mapped[Optional[str]] = mapped_column(Text)
    shap_values_path: Mapped[Optional[str]] = mapped_column(Text)
    feature_importance_path: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        Enum("active", "archived", "training", "failed", name="model_status"),
        nullable=False, default="archived"
    )

    dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_datasets.id", ondelete="SET NULL"))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    notes: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSONB, default=list)

    training_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    promoted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    dataset = relationship("UploadedDataset", back_populates="model_registry")
    predictions = relationship("Prediction", back_populates="model")
    training_history = relationship("TrainingHistory", back_populates="model_registry")


# ============================================================
# TrainingHistory
# ============================================================
class TrainingHistory(Base):
    __tablename__ = "training_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_datasets.id", ondelete="SET NULL"))
    model_registry_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("model_registry.id", ondelete="SET NULL"))

    algorithms_trained: Mapped[list] = mapped_column(JSONB, default=list)
    training_config: Mapped[dict] = mapped_column(JSONB, default=dict)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)

    best_algorithm: Mapped[Optional[str]] = mapped_column(String(100))
    best_f1_score: Mapped[Optional[float]] = mapped_column(Float)
    all_results: Mapped[dict] = mapped_column(JSONB, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    log_output: Mapped[Optional[str]] = mapped_column(Text)

    triggered_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    is_auto_retrain: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    dataset = relationship("UploadedDataset", back_populates="training_history")
    model_registry = relationship("ModelRegistry", back_populates="training_history")


# ============================================================
# Prediction
# ============================================================
class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"))
    model_registry_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("model_registry.id", ondelete="SET NULL"))

    input_features: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    attrition_probability: Mapped[float] = mapped_column(Float, nullable=False)
    attrition_prediction: Mapped[str] = mapped_column(Enum("Yes", "No", name="attrition_type2"), nullable=False)
    risk_level: Mapped[str] = mapped_column(Enum("Low", "Medium", "High", "Critical", name="risk_level"), nullable=False)

    shap_values: Mapped[dict] = mapped_column(JSONB, default=dict)
    top_risk_factors: Mapped[list] = mapped_column(JSONB, default=list)
    retention_recommendations: Mapped[list] = mapped_column(JSONB, default=list)
    explanation_text: Mapped[Optional[str]] = mapped_column(Text)
    shap_plot_path: Mapped[Optional[str]] = mapped_column(Text)
    waterfall_plot_path: Mapped[Optional[str]] = mapped_column(Text)

    prediction_type: Mapped[str] = mapped_column(String(20), default="individual")
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    predicted_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    actual_attrition: Mapped[Optional[str]] = mapped_column(String(3))
    feedback_given_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="predictions")
    model = relationship("ModelRegistry", back_populates="predictions")
    predicted_by_user = relationship("User", back_populates="predictions", foreign_keys=[predicted_by])


# ============================================================
# Report
# ============================================================
class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    format: Mapped[str] = mapped_column(Enum("pdf", "excel", "csv", "pptx", name="report_format"), nullable=False)
    status: Mapped[str] = mapped_column(Enum("pending", "generating", "completed", "failed", name="report_status"), nullable=False, default="pending")

    file_path: Mapped[Optional[str]] = mapped_column(Text)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    download_url: Mapped[Optional[str]] = mapped_column(Text)

    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False)
    schedule_cron: Mapped[Optional[str]] = mapped_column(String(100))
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    email_delivery: Mapped[bool] = mapped_column(Boolean, default=False)
    recipient_emails: Mapped[list] = mapped_column(JSONB, default=list)

    filters: Mapped[dict] = mapped_column(JSONB, default=dict)
    job_id: Mapped[Optional[str]] = mapped_column(String(100))
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_datasets.id", ondelete="SET NULL"))
    model_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("model_registry.id", ondelete="SET NULL"))
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    created_by_user = relationship("User", back_populates="reports")


# ============================================================
# AuditLog
# ============================================================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100))
    resource_id: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    request_method: Mapped[Optional[str]] = mapped_column(String(10))
    request_path: Mapped[Optional[str]] = mapped_column(Text)
    response_status: Mapped[Optional[int]] = mapped_column(Integer)
    audit_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
