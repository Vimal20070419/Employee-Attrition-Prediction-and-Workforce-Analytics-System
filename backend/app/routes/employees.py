"""
AttritionIQ — Employees Routes
=================================
CRUD for employees with pagination, filtering, sorting, and search.
"""

import uuid
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_cache.decorator import cache
from sqlalchemy import func, or_, select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac import require_any_authenticated, require_hr_analyst, require_hr_manager
from app.database import get_db
from app.models.employee import Employee
from app.models.models import Department
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate, EmployeeListResponse
from app.utils.audit import log_audit
from app.utils.pagination import PaginationParams, paginate_query

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("", response_model=EmployeeListResponse)
@cache(expire=60)
async def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by job_role or employee_number"),
    department_id: Optional[uuid.UUID] = Query(None),
    attrition: Optional[str] = Query(None, pattern="^(Yes|No)$"),
    risk_level: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|age|monthly_income|years_at_company)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> EmployeeListResponse:
    """List all employees with filtering, sorting, and pagination."""

    query = select(Employee).where(Employee.is_active == True)

    # Filters
    if search:
        query = query.where(
            or_(
                Employee.job_role.ilike(f"%{search}%"),
                Employee.employee_number.ilike(f"%{search}%"),
            )
        )
    if department_id:
        query = query.where(Employee.department_id == department_id)
    if attrition:
        query = query.where(Employee.attrition == attrition)
    if gender:
        query = query.where(Employee.gender == gender)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Sort
    sort_col = getattr(Employee, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_col))
    else:
        query = query.order_by(asc(sort_col))

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    employees = result.scalars().all()

    return EmployeeListResponse(
        items=employees,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_analyst),
) -> EmployeeResponse:
    """Create a new employee record."""

    employee = Employee(**employee_data.model_dump(), created_by=current_user.id)
    db.add(employee)
    await db.flush()
    await log_audit(db, current_user.id, "create", "employee", str(employee.id))
    await db.commit()
    await db.refresh(employee)
    return employee


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> EmployeeResponse:
    """Get employee by ID."""

    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: uuid.UUID,
    employee_data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_analyst),
) -> EmployeeResponse:
    """Update employee record."""

    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    update_data = employee_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)

    await log_audit(db, current_user.id, "update", "employee", str(employee_id))
    await db.commit()
    await db.refresh(employee)
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_manager),
) -> None:
    """Soft-delete an employee (sets is_active=False)."""

    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    employee.is_active = False
    await log_audit(db, current_user.id, "delete", "employee", str(employee_id))
    await db.commit()


@router.get("/stats/summary")
@cache(expire=300)
async def get_employee_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Get summary statistics for dashboard KPI cards."""

    total = await db.scalar(select(func.count(Employee.id)).where(Employee.is_active == True))
    attrition_yes = await db.scalar(
        select(func.count(Employee.id)).where(Employee.attrition == "Yes", Employee.is_active == True)
    )
    avg_income = await db.scalar(select(func.avg(Employee.monthly_income)).where(Employee.is_active == True))
    avg_age = await db.scalar(select(func.avg(Employee.age)).where(Employee.is_active == True))
    avg_years = await db.scalar(select(func.avg(Employee.years_at_company)).where(Employee.is_active == True))

    attrition_rate = round((attrition_yes / total * 100), 2) if total else 0

    return {
        "total_employees": total or 0,
        "current_employees": (total - (attrition_yes or 0)) if total else 0,
        "employees_left": attrition_yes or 0,
        "attrition_rate_pct": attrition_rate,
        "avg_monthly_income": round(float(avg_income or 0), 2),
        "avg_age": round(float(avg_age or 0), 1),
        "avg_years_at_company": round(float(avg_years or 0), 1),
    }
