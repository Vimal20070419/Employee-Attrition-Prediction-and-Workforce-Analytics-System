"""AttritionIQ — Analytics Schemas"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class KPISummary(BaseModel):
    total_employees: int
    current_employees: int
    employees_left: int
    attrition_rate_pct: float
    avg_monthly_salary: float
    avg_age: float
    avg_years_at_company: float
    avg_job_satisfaction: float


class DepartmentRiskScore(BaseModel):
    department: str
    avg_risk_score: float
    prediction_count: int
    risk_category: str


class AttritionTrendPoint(BaseModel):
    month: str
    total: int
    attrited: int
    attrition_rate: float


class DashboardOverviewResponse(BaseModel):
    kpis: KPISummary
    departments: List[Dict]
    gender_distribution: Dict[str, int]
    risk_distribution: Dict[str, int]
    model_performance: Optional[Dict]
    high_risk_employees: List[Dict]
