# File: app/api/v1/resume.py
"""
RESUME API ENDPOINTS - FastAPI routes for resume processing and job applications

This module defines all the HTTP endpoints that clients can use to interact with
the AI job application system. It's the "front door" of your system that handles
web requests and coordinates between different services.

Available Endpoints:
- POST /upload - Upload and process resume PDFs
- GET /embedding - Get the current resume embedding
- POST /tailor - Generate tailored resume for specific job
- GET /download - Download generated resume PDFs
- POST /apply - Auto-apply to job (basic Ashby method)
- POST /form/map - Map job application form fields using AI
- POST /apply/intelligent - Apply using AI-mapped form fields
- POST /log - Manual Notion logging
- POST /log/auto - Automatic project update logging

Each endpoint handles HTTP requests, validates inputs, calls appropriate services,
and returns JSON responses with results or error information.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import os
from app.services.resume_parser import extract_text_from_resume, embed_resume_text
from app.services.resume_tailor import tailor_resume
from app.services.pdf_generator import save_resume_as_pdf
from app.services.form_autofiller import apply_to_ashby_job
from app.services.field_mapper import extract_form_selectors
from app.services.form_executor import fill_fields
from playwright.sync_api import sync_playwright
from app.services.notion_logger import log_to_notion, auto_log_project_update


router = APIRouter()

# Ensure upload directory exists for storing files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global variable to cache the most recent resume embedding
# This avoids re-processing the same resume multiple times
latest_embedding = None

# === PYDANTIC MODELS FOR REQUEST/RESPONSE VALIDATION ===

class ResumeTailorRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: str
    company_name: str

class AutoApplyRequest(BaseModel):
    """
    Request model for automated job applications
    
    This validates applicant information and resume file
    for automated form filling and submission.
    """
    job_url: str          # URL of the job application page
    name: str             # Applicant's full name
    email: str            # Applicant's email address
    phone: str            # Applicant's phone number
    resume_filename: str  # Name of uploaded resume file

class FormMapRequest(BaseModel):
    """
    Request model for form field mapping
    
    Simple model that just needs the job URL to analyze
    the application form structure.
    """
    job_url: str          # URL of job application page to analyze

# === RESUME PROCESSING ENDPOINTS ===

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    global latest_embedding
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        # Save uploaded file to disk
        with open(file_path, "wb") as f:
            content = await file.read()  # Read file content from request
            f.write(content)

        # Extract text from the PDF using PyMuPDF
        raw_text = extract_text_from_resume(file_path)
        
        # Generate AI embedding using OpenAI API
        embedding = embed_resume_text(raw_text)
        
        # Cache embedding for use in other endpoints
        latest_embedding = embedding

        # Return success response with preview data
        return JSONResponse({
            "message": "Resume processed successfully",
            "raw_text_snippet": raw_text[:300],  # First 300 chars for preview
            "embedding_preview": embedding[:5]   # First 5 embedding values
        })

    except Exception as e:
        # Return error response if anything fails
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/embedding")
def get_latest_embedding():
    if not latest_embedding:
        raise HTTPException(status_code=404, detail="No embedding available. Upload a resume first.")
    
    return {"embedding": latest_embedding}

# === RESUME TAILORING ENDPOINTS ===

@router.post("/tailor")
def tailor_resume_endpoint(payload: ResumeTailorRequest):
    try:
        # Use GPT-4 to tailor resume for the specific job
        tailored = tailor_resume(payload.resume_text, payload.job_description)
        
        # Create personalized filename for the tailored resume PDF
        # Extract name from first line of resume, clean up spaces
        name_part = payload.resume_text.splitlines()[0].replace(' ', '_')
        job_part = payload.job_title.replace(' ', '_')
        company_part = payload.company_name.replace(' ', '_')
        filename = f"{name_part}_for_{job_part}_at_{company_part}.pdf"
        
        # Generate PDF version of the tailored resume
        pdf_path = save_resume_as_pdf(tailored, filename=filename)
        
        return {
            "tailored_resume": tailored,
            "pdf_download_path": pdf_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download")
def download_pdf(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found.")
    
    # Return file with proper headers for download
    return FileResponse(path=file_path, filename=filename, media_type='application/pdf')

# === JOB APPLICATION ENDPOINTS ===

@router.post("/apply")
def auto_apply(payload: AutoApplyRequest):
    resume_path = os.path.join(UPLOAD_DIR, payload.resume_filename)
    if not os.path.exists(resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found.")

    # Use Ashby-specific form filling logic
    result = apply_to_ashby_job(
        url=payload.job_url,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        resume_path=resume_path
    )

    return result

@router.post("/form/map")
def form_map(payload: FormMapRequest):
    try:
        # Use AI to analyze form structure and create field mapping
        result = extract_form_selectors(payload.job_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply/intelligent")
def apply_intelligent(payload: AutoApplyRequest):
    resume_path = os.path.join(UPLOAD_DIR, payload.resume_filename)
    if not os.path.exists(resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found.")

    # Step 1: Get AI-generated form field mapping
    map_result = extract_form_selectors(payload.job_url)
    if map_result["status"] != "success":
        return map_result

    # Step 2: Parse JSON mapping from GPT-4 response
    import re, json
    # Try to extract JSON from markdown code block
    match = re.search(r"```json\n(.*?)```", map_result["selector_map"], re.DOTALL)
    if match:
        selector_map = json.loads(match.group(1))
    else:
        raise HTTPException(status_code=500, detail="Could not extract valid JSON selector map.")
    
    # Step 3: Prepare applicant data for form filling
    data = {
        key: value for key, value in {
            "full_name": payload.name,
            "_systemfield_name": payload.name,
            "email": payload.email,
            "_systemfield_email": payload.email,
            "phone": payload.phone,
            "_systemfield_phone": payload.phone
        }.items() if value
    }

    screenshot_path = "uploads/intelligent_apply.png"

    # Step 4: Execute form filling with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible browser for debugging
        page = browser.new_page()
        try:
            # Load the job application page
            page.goto(payload.job_url, timeout=60000)
            page.wait_for_timeout(3000)  # Wait for page to fully load

            # Use form executor to fill all mapped fields
            field_results = fill_fields(page, selector_map, data, resume_path)

            # Take screenshot for verification
            page.screenshot(path=screenshot_path)
            
            return {
                "status": "success",
                "fields": field_results,
                "screenshot": screenshot_path
            }
        except Exception as e:
            # Take error screenshot for debugging
            page.screenshot(path="uploads/intelligent_error.png")
            return {"status": "error", "error": str(e)}
        finally:
            browser.close()

# === NOTION LOGGING ENDPOINTS ===

class NotionLogRequest(BaseModel):
    """
    Request model for manual Notion logging
    
    Allows clients to create custom log entries in Notion
    """
    title: str      # Title for the Notion page
    content: str    # Content for the Notion page

@router.post("/log")
def log_to_notion_route(payload: NotionLogRequest):
    try:
        return log_to_notion(payload.title, payload.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log/auto")
def auto_log_to_notion_route():
    try:
        return auto_log_project_update()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

