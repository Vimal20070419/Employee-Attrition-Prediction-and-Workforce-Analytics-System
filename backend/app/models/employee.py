"""
AttritionIQ — Employee ORM Model
"""

import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Employee(Base):
    """Employee record with full IBM HR dataset fields."""

    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True)

    # Personal Info
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(Enum("Male", "Female", "Other", name="gender_type"), nullable=False)
    marital_status: Mapped[Optional[str]] = mapped_column(String(20))
    education: Mapped[Optional[int]] = mapped_column(Integer)
    education_field: Mapped[Optional[str]] = mapped_column(String(50))
    distance_from_home: Mapped[Optional[int]] = mapped_column(Integer)

    # Job Info
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), index=True
    )
    job_role: Mapped[str] = mapped_column(String(100), nullable=False)
    job_level: Mapped[Optional[int]] = mapped_column(Integer)
    job_involvement: Mapped[Optional[int]] = mapped_column(Integer)

    # Compensation
    monthly_income: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    hourly_rate: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))
    daily_rate: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))
    monthly_rate: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    percent_salary_hike: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    stock_option_level: Mapped[Optional[int]] = mapped_column(Integer)

    # Work Details
    over_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    business_travel: Mapped[Optional[str]] = mapped_column(String(50))
    num_companies_worked: Mapped[Optional[int]] = mapped_column(Integer)

    # Tenure
    total_working_years: Mapped[Optional[int]] = mapped_column(Integer)
    years_at_company: Mapped[Optional[int]] = mapped_column(Integer)
    years_in_current_role: Mapped[Optional[int]] = mapped_column(Integer)
    years_since_last_promotion: Mapped[Optional[int]] = mapped_column(Integer)
    years_with_curr_manager: Mapped[Optional[int]] = mapped_column(Integer)
    training_times_last_year: Mapped[Optional[int]] = mapped_column(Integer)

    # Satisfaction (1-4)
    environment_satisfaction: Mapped[Optional[int]] = mapped_column(Integer)
    job_satisfaction: Mapped[Optional[int]] = mapped_column(Integer)
    relationship_satisfaction: Mapped[Optional[int]] = mapped_column(Integer)
    work_life_balance: Mapped[Optional[int]] = mapped_column(Integer)

    # Performance
    performance_rating: Mapped[Optional[int]] = mapped_column(Integer)

    # Outcome
    attrition: Mapped[Optional[str]] = mapped_column(Enum("Yes", "No", name="attrition_type"))

    # Meta
    hire_date: Mapped[Optional[date]] = mapped_column(Date)
    termination_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), index=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    department = relationship("Department", back_populates="employees")
    predictions = relationship("Prediction", back_populates="employee")

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, role={self.job_role}, attrition={self.attrition})>"
