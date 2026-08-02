"""AttritionIQ — Employee + Prediction Pydantic Schemas"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Employee Schemas
# ─────────────────────────────────────────────
class EmployeeCreate(BaseModel):
    age: int = Field(ge=18, le=70)
    gender: str
    marital_status: Optional[str] = None
    education: Optional[int] = Field(None, ge=1, le=5)
    education_field: Optional[str] = None
    distance_from_home: Optional[int] = Field(None, ge=0)
    department_id: Optional[uuid.UUID] = None
    job_role: str
    job_level: Optional[int] = Field(None, ge=1, le=5)
    job_involvement: Optional[int] = Field(None, ge=1, le=4)
    monthly_income: float = Field(gt=0)
    over_time: bool = False
    business_travel: Optional[str] = None
    num_companies_worked: Optional[int] = Field(None, ge=0)
    total_working_years: Optional[int] = Field(None, ge=0)
    years_at_company: Optional[int] = Field(None, ge=0)
    years_in_current_role: Optional[int] = Field(None, ge=0)
    years_since_last_promotion: Optional[int] = Field(None, ge=0)
    years_with_curr_manager: Optional[int] = Field(None, ge=0)
    training_times_last_year: Optional[int] = Field(None, ge=0)
    environment_satisfaction: Optional[int] = Field(None, ge=1, le=4)
    job_satisfaction: Optional[int] = Field(None, ge=1, le=4)
    relationship_satisfaction: Optional[int] = Field(None, ge=1, le=4)
    work_life_balance: Optional[int] = Field(None, ge=1, le=4)
    performance_rating: Optional[int] = Field(None, ge=1, le=4)
    attrition: Optional[str] = None


class EmployeeUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=18, le=70)
    gender: Optional[str] = None
    monthly_income: Optional[float] = Field(None, gt=0)
    over_time: Optional[bool] = None
    environment_satisfaction: Optional[int] = Field(None, ge=1, le=4)
    job_satisfaction: Optional[int] = Field(None, ge=1, le=4)
    performance_rating: Optional[int] = Field(None, ge=1, le=4)
    work_life_balance: Optional[int] = Field(None, ge=1, le=4)
    attrition: Optional[str] = None


class EmployeeResponse(BaseModel):
    id: uuid.UUID
    employee_number: Optional[str]
    age: int
    gender: str
    job_role: str
    monthly_income: float
    over_time: bool
    years_at_company: Optional[int]
    attrition: Optional[str]
    department_id: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    items: List[EmployeeResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ─────────────────────────────────────────────
# Prediction Schemas
# ─────────────────────────────────────────────
class PredictionRequest(BaseModel):
    employee_id: Optional[uuid.UUID] = None
    age: int = Field(ge=18, le=70)
    gender: str
    marital_status: Optional[str] = None
    education: Optional[int] = Field(None, ge=1, le=5)
    education_field: Optional[str] = None
    department: Optional[str] = None
    job_role: str
    job_level: Optional[int] = Field(None, ge=1, le=5)
    monthly_income: float = Field(gt=0)
    over_time: bool = False
    business_travel: Optional[str] = None
    distance_from_home: Optional[int] = Field(None, ge=0)
    num_companies_worked: Optional[int] = Field(None, ge=0)
    total_working_years: Optional[int] = Field(None, ge=0)
    years_at_company: Optional[int] = Field(None, ge=0)
    years_in_current_role: Optional[int] = Field(None, ge=0)
    years_since_last_promotion: Optional[int] = Field(None, ge=0)
    years_with_curr_manager: Optional[int] = Field(None, ge=0)
    training_times_last_year: Optional[int] = Field(None, ge=0)
    environment_satisfaction: Optional[int] = Field(None, ge=1, le=4)
    job_satisfaction: Optional[int] = Field(None, ge=1, le=4)
    relationship_satisfaction: Optional[int] = Field(None, ge=1, le=4)
    work_life_balance: Optional[int] = Field(None, ge=1, le=4)
    performance_rating: Optional[int] = Field(None, ge=1, le=4)
    stock_option_level: Optional[int] = Field(None, ge=0, le=3)
    job_involvement: Optional[int] = Field(None, ge=1, le=4)
    percent_salary_hike: Optional[float] = None


class PredictionResponse(BaseModel):
    id: uuid.UUID
    employee_id: Optional[uuid.UUID]
    attrition_probability: float
    attrition_prediction: str
    risk_level: str
    top_risk_factors: list
    retention_recommendations: list
    explanation_text: Optional[str]
    shap_values: dict
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionListResponse(BaseModel):
    items: List[PredictionResponse]
    total: int
    page: int
    page_size: int
    pages: int


class BatchPredictionRequest(BaseModel):
    employee_ids: List[uuid.UUID]


class FeedbackRequest(BaseModel):
    actual_attrition: str = Field(pattern="^(Yes|No)$")
