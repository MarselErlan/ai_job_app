# File: app/api/v1/pipeline.py
"""
PIPELINE API ENDPOINT - Web interface for running the complete job application pipeline

This module provides the HTTP API endpoint that allows external applications
(like web frontends, mobile apps, or other services) to trigger the complete
job application pipeline through a simple POST request.

Endpoints:
- POST /api/v1/pipeline/start         : Runs pipeline for a single best match
- POST /api/v1/pipeline/apply-multi   : Runs pipeline for top 5 matches

This is essentially a web wrapper around the core pipeline functionality,
making it accessible through HTTP requests with proper validation and error handling.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from app.tasks.pipeline import run_pipeline
from app.tasks.pipeline_for_5 import run_pipeline_multi_apply

# Create a router for pipeline-related endpoints
router = APIRouter()

# Request model for pipeline execution
class PipelineRequest(BaseModel):
    resume_filename: str
    name: str
    email: str
    phone: str
    role: str
    location: str

@router.post("/start")
def start_pipeline(request: PipelineRequest):
    file_path = os.path.join("uploads", request.resume_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")

    result = run_pipeline(
        file_path=file_path,
        name=request.name,
        email=request.email,
        phone=request.phone,
        role=request.role,
        location=request.location
    )
    return result

@router.post("/pipeline/apply-multi")
def apply_to_multiple_jobs(request: PipelineRequest):
    file_path = os.path.join("uploads", request.resume_filename)
    
    # Verify the resume file actually exists before proceeding
    # This prevents the pipeline from starting with invalid input
    if not os.path.exists(file_path):
        # Raise HTTP 404 error if file not found
        # FastAPI automatically converts this to proper HTTP response
        raise HTTPException(status_code=404, detail="Resume file not found")
    result = run_pipeline_multi_apply(
        file_path=file_path,      # Full path to the resume PDF
        name=request.name,        # Applicant's name for form filling
        email=request.email,      # Email for job applications
        phone=request.phone,      # Phone for job applications
        role=request.role,        # Role for job applications
        location=request.location # Location for job applications
    )
    return result

