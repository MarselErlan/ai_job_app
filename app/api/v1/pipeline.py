# File: app/api/v1/pipeline.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from app.tasks.pipeline import run_pipeline

router = APIRouter()

class PipelineRequest(BaseModel):
    resume_filename: str
    name: str
    email: str
    phone: str

@router.post("/start")
def start_pipeline(request: PipelineRequest):
    file_path = os.path.join("uploads", request.resume_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")

    result = run_pipeline(
        file_path=file_path,
        name=request.name,
        email=request.email,
        phone=request.phone
    )

    return result
