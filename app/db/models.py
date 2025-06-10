# File: app/db/models.py

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, nullable=False)
    job_url = Column(String, nullable=False, unique=True)  # Prevent duplicate applications
    company_name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    applied = Column(Boolean, default=False)
    status = Column(String, default="pending")  # Options: pending, applied, failed
    resume_used = Column(String, nullable=True)  # Store filename or unique resume ID
    notes = Column(Text, nullable=True)
    screenshot_path = Column(String, nullable=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('job_url', name='uq_job_url'),
    )

