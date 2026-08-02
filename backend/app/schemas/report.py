"""AttritionIQ — Report Schemas"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class ReportCreate(BaseModel):
    title: str
    report_type: str
    format: str  # pdf, excel, csv, pptx
    is_scheduled: bool = False
    cron_schedule: Optional[str] = None
    email_delivery: bool = False
    recipient_emails: Optional[List[EmailStr]] = None
    filters: Optional[Dict] = None


class ReportResponse(BaseModel):
    id: uuid.UUID
    title: str
    report_type: str
    format: str
    status: str
    file_path: Optional[str]
    file_size_bytes: Optional[int]
    download_url: Optional[str]
    is_scheduled: bool
    cron_schedule: Optional[str]
    email_delivery: bool
    recipient_emails: Optional[List[str]]
    last_run_at: Optional[datetime]
    created_at: datetime
    error_message: Optional[str]

    class Config:
        from_attributes = True
