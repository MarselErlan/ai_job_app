# File: app/schemas/job.py

from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class JobApplicationCreate(BaseModel):
    job_title: str
    job_url: HttpUrl
    company_name: Optional[str] = None
    location: Optional[str] = None
    resume_used: Optional[str] = None

class JobApplicationResponse(JobApplicationCreate):
    id: int
    applied: bool
    status: str
    screenshot_path: Optional[str]
    notes: Optional[str]
    applied_at: datetime

    class Config:
        orm_mode = True
