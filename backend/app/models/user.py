"""
AttritionIQ — User ORM Model
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, String, Text, JSON, UUID
JSONB = JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """Platform user with role-based access control."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)

    role: Mapped[str] = mapped_column(
        Enum("admin", "hr_manager", "hr_analyst", "viewer", name="user_role"),
        nullable=False,
        default="viewer",
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "inactive", "suspended", "pending_verification", name="user_status"),
        nullable=False,
        default="pending_verification",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    job_title: Mapped[Optional[str]] = mapped_column(String(100))

    # Email verification
    email_verification_token: Mapped[Optional[str]] = mapped_column(Text)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Password reset
    password_reset_token: Mapped[Optional[str]] = mapped_column(Text)
    password_reset_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Refresh token
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Preferences
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Timestamps
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    predictions = relationship("Prediction", back_populates="predicted_by_user", foreign_keys="Prediction.predicted_by")
    audit_logs = relationship("AuditLog", back_populates="user")
    reports = relationship("Report", back_populates="created_by_user")
    datasets = relationship("UploadedDataset", back_populates="uploaded_by_user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
