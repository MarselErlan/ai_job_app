# File: app/api/v1/resume.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
from app.services.resume_parser import extract_text_from_resume, embed_resume_text

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract + Embed
        raw_text = extract_text_from_resume(file_path)
        embedding = embed_resume_text(raw_text)

        return JSONResponse({
            "message": "Resume processed successfully",
            "raw_text_snippet": raw_text[:300],
            "embedding_preview": embedding[:5]  # first 5 dims
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
