# File: app/api/v1/resume.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from app.services.resume_parser import extract_text_from_resume, embed_resume_text
from app.services.resume_tailor import tailor_resume

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

latest_embedding = None  # Global cache for current session

class ResumeTailorRequest(BaseModel):
    resume_text: str
    job_description: str

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    global latest_embedding
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract + Embed
        raw_text = extract_text_from_resume(file_path)
        embedding = embed_resume_text(raw_text)
        latest_embedding = embedding

        return JSONResponse({
            "message": "Resume processed successfully",
            "raw_text_snippet": raw_text[:300],
            "embedding_preview": embedding[:5]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/embedding")
def get_latest_embedding():
    if not latest_embedding:
        raise HTTPException(status_code=404, detail="No embedding available. Upload a resume first.")
    return {"embedding": latest_embedding}

@router.post("/tailor")
def tailor_resume_endpoint(payload: ResumeTailorRequest):
    try:
        tailored = tailor_resume(payload.resume_text, payload.job_description)
        return {"tailored_resume": tailored}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
