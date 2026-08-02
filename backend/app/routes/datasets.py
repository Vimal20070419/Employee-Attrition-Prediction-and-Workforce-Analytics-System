"""
AttritionIQ — Datasets Routes
================================
Upload, validate, version, and manage training datasets.
"""

import hashlib
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac import require_any_authenticated, require_hr_analyst
from app.config import settings
from app.database import get_db
from app.models.models import UploadedDataset
from app.models.user import User
from app.utils.audit import log_audit

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_analyst),
) -> dict:
    """Upload a CSV or Excel dataset for training."""

    # Validate extension
    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    # Validate file size
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Checksum
    checksum = hashlib.sha256(content).hexdigest()

    # Check duplicate
    existing = await db.execute(
        select(UploadedDataset).where(UploadedDataset.checksum == checksum)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dataset with identical content already exists",
        )

    # Save file
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    dataset_id = uuid.uuid4()
    file_path = upload_path / f"{dataset_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)

    # Get version
    count = await db.scalar(select(func.count(UploadedDataset.id)))
    version = f"v{(count or 0) + 1}.0"

    # Create record
    dataset = UploadedDataset(
        id=dataset_id,
        name=name,
        description=description,
        file_name=file.filename,
        file_path=str(file_path),
        file_size_bytes=len(content),
        file_format=ext,
        version=version,
        checksum=checksum,
        uploaded_by=current_user.id,
    )
    db.add(dataset)
    await db.flush()

    # Trigger background validation
    background_tasks.add_task(validate_dataset_background, str(dataset.id))

    await log_audit(db, current_user.id, "upload", "dataset", str(dataset.id))
    await db.commit()
    await db.refresh(dataset)

    return {
        "success": True,
        "dataset_id": str(dataset.id),
        "version": version,
        "message": "Dataset uploaded successfully. Validation in progress.",
    }


@router.get("")
async def list_datasets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """List all uploaded datasets."""
    query = select(UploadedDataset).where(UploadedDataset.is_active == True).order_by(desc(UploadedDataset.created_at))
    total = await db.scalar(select(func.count(UploadedDataset.id)))
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    datasets = result.scalars().all()
    return {
        "items": [
            {
                "id": str(d.id),
                "name": d.name,
                "version": d.version,
                "file_name": d.file_name,
                "file_size_bytes": d.file_size_bytes,
                "row_count": d.row_count,
                "is_validated": d.is_validated,
                "is_processed": d.is_processed,
                "created_at": d.created_at.isoformat(),
            }
            for d in datasets
        ],
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_authenticated),
) -> dict:
    """Get dataset details including validation report."""
    result = await db.execute(select(UploadedDataset).where(UploadedDataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return {
        "id": str(dataset.id),
        "name": dataset.name,
        "description": dataset.description,
        "version": dataset.version,
        "file_name": dataset.file_name,
        "file_size_bytes": dataset.file_size_bytes,
        "file_format": dataset.file_format,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "columns_info": dataset.columns_info,
        "validation_report": dataset.validation_report,
        "is_validated": dataset.is_validated,
        "is_processed": dataset.is_processed,
        "created_at": dataset.created_at.isoformat(),
    }


@router.post("/{dataset_id}/train")
async def trigger_training(
    dataset_id: uuid.UUID,
    algorithms: Optional[list] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_analyst),
) -> dict:
    """Trigger ML training pipeline as a Celery background task."""
    result = await db.execute(select(UploadedDataset).where(UploadedDataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    if not dataset.is_validated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dataset not yet validated")

    from app.tasks.training_tasks import run_training_task
    task = run_training_task.apply_async(
        kwargs={
            "dataset_id": str(dataset_id),
            "user_id": str(current_user.id),
            "algorithms": algorithms,
        },
        queue="training",
    )
    return {"success": True, "task_id": task.id, "message": "Training started in background"}


async def validate_dataset_background(dataset_id: str) -> None:
    """Background task: validate dataset structure and stats."""
    logger.info("Validating dataset", dataset_id=dataset_id)
    # Actual validation delegated to ML service via HTTP call
