# File: app/db/crud.py

from sqlalchemy.orm import Session
from app.db.models import JobApplication

def get_all_job_urls(db: Session):
    return {row.job_url for row in db.query(JobApplication.job_url).all()}

def create_job_entry(db: Session, job: dict):
    db_job = JobApplication(
        job_title=job.get("title"),
        job_url=job.get("url"),
        company_name=None,  # Can be extracted later
        location=None,
        applied=False,
        status="pending"
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
