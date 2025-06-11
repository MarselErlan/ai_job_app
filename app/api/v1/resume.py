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
from loguru import logger
from app.utils.debug_utils import debug_performance

# Configure Loguru
logger.add(
    "logs/resume_api.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
)

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
@debug_performance
async def upload_resume(file: UploadFile = File(...)):
    """Process and embed an uploaded resume PDF."""
    global latest_embedding
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    logger.info(f"Processing resume upload: {file.filename}")

    try:
        # Save uploaded file to disk
        logger.debug(f"Saving uploaded file to: {file_path}")
        with open(file_path, "wb") as f:
            content = await file.read()  # Read file content from request
            f.write(content)
        logger.debug(f"File saved successfully, size: {len(content)} bytes")

        # Extract text from the PDF using PyMuPDF
        logger.debug("Extracting text from PDF")
        raw_text = extract_text_from_resume(file_path)
        logger.debug(f"Extracted text length: {len(raw_text)} characters")
        
        # Generate AI embedding using OpenAI API
        logger.debug("Generating resume embedding")
        embedding = embed_resume_text(raw_text)
        
        # Cache embedding for use in other endpoints
        latest_embedding = embedding
        logger.info("Resume processed and embedded successfully")

        # Return success response with preview data
        return JSONResponse({
            "message": "Resume processed successfully",
            "raw_text_snippet": raw_text[:300],  # First 300 chars for preview
            "embedding_preview": embedding[:5]   # First 5 embedding values
        })

    except Exception as e:
        logger.error(f"Error processing resume upload: {str(e)}")
        # Return error response if anything fails
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/embedding")
@debug_performance
def get_latest_embedding():
    """Retrieve the most recently generated resume embedding."""
    logger.debug("Retrieving latest resume embedding")
    if not latest_embedding:
        logger.warning("No embedding available - no resume has been uploaded")
        raise HTTPException(status_code=404, detail="No embedding available. Upload a resume first.")
    
    logger.info("Successfully retrieved latest embedding")
    return {"embedding": latest_embedding}

# === RESUME TAILORING ENDPOINTS ===

@router.post("/tailor")
@debug_performance
def tailor_resume_endpoint(payload: ResumeTailorRequest):
    """Generate a tailored version of the resume for a specific job."""
    logger.info(f"Tailoring resume for {payload.job_title} at {payload.company_name}")
    
    try:
        # Use GPT-4 to tailor resume for the specific job
        logger.debug("Starting resume tailoring process")
        tailored = tailor_resume(payload.resume_text, payload.job_description)
        logger.debug(f"Tailored resume length: {len(tailored)} characters")
        
        # Create personalized filename for the tailored resume PDF
        # Extract name from first line of resume, clean up spaces
        name_part = payload.resume_text.splitlines()[0].replace(' ', '_')
        job_part = payload.job_title.replace(' ', '_')
        company_part = payload.company_name.replace(' ', '_')
        filename = f"{name_part}_for_{job_part}_at_{company_part}.pdf"
        logger.debug(f"Generated PDF filename: {filename}")
        
        # Generate PDF version of the tailored resume
        logger.debug("Generating PDF from tailored resume")
        pdf_path = save_resume_as_pdf(tailored, filename=filename)
        logger.info(f"Successfully generated tailored resume PDF: {pdf_path}")
        
        return {
            "tailored_resume": tailored,
            "pdf_download_path": pdf_path
        }
    except Exception as e:
        logger.error(f"Error during resume tailoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download")
@debug_performance
def download_pdf(filename: str):
    """Download a generated PDF resume."""
    logger.info(f"Processing PDF download request: {filename}")
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        logger.warning(f"Requested PDF not found: {file_path}")
        raise HTTPException(status_code=404, detail="PDF not found.")
    
    logger.debug(f"Serving PDF file: {file_path}")
    # Return file with proper headers for download
    return FileResponse(path=file_path, filename=filename, media_type='application/pdf')

# === JOB APPLICATION ENDPOINTS ===

@router.post("/apply")
@debug_performance
def auto_apply(payload: AutoApplyRequest):
    """Submit a job application using the Ashby ATS method."""
    logger.info(f"Processing auto-apply request for {payload.name} to {payload.job_url}")
    
    resume_path = os.path.join(UPLOAD_DIR, payload.resume_filename)
    if not os.path.exists(resume_path):
        logger.error(f"Resume file not found: {resume_path}")
        raise HTTPException(status_code=404, detail="Resume file not found.")

    logger.debug("Starting Ashby application process")
    # Use Ashby-specific form filling logic
    result = apply_to_ashby_job(
        url=payload.job_url,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        resume_path=resume_path
    )

    logger.info("Auto-apply process completed")
    return result

@router.post("/form/map")
@debug_performance
def form_map(payload: FormMapRequest):
    """Analyze and map form fields using AI."""
    logger.info(f"Mapping form fields for URL: {payload.job_url}")
    
    try:
        # Use AI to analyze form structure and create field mapping
        logger.debug("Starting form field extraction")
        result = extract_form_selectors(payload.job_url)
        logger.info("Successfully mapped form fields")
        return result
    except Exception as e:
        logger.error(f"Error mapping form fields: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply/intelligent")
@debug_performance
def apply_intelligent(payload: AutoApplyRequest):
    """Submit a job application using AI-powered form field mapping."""
    logger.info(f"Processing intelligent apply request for {payload.name} to {payload.job_url}")
    
    resume_path = os.path.join(UPLOAD_DIR, payload.resume_filename)
    if not os.path.exists(resume_path):
        logger.error(f"Resume file not found: {resume_path}")
        raise HTTPException(status_code=404, detail="Resume file not found.")

    try:
        # Step 1: Get AI-generated form field mapping
        logger.debug("Getting form field mapping")
        map_result = extract_form_selectors(payload.job_url)
        if map_result["status"] != "success":
            logger.error("Form mapping failed")
            return map_result

        # Step 2: Parse JSON mapping from GPT-4 response
        logger.debug("Parsing field mapping JSON")
        import re, json
        # Try to extract JSON from markdown code block
        match = re.search(r"```json\n(.*?)```", map_result["selector_map"], re.DOTALL)
        if match:
            selector_map = json.loads(match.group(1))
            logger.debug(f"Successfully parsed {len(selector_map)} field mappings")
        else:
            logger.error("Failed to extract valid JSON selector map")
            raise HTTPException(status_code=500, detail="Could not extract valid JSON selector map.")
        
        # Step 3: Prepare applicant data for form filling
        logger.debug("Preparing applicant data")
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
        logger.debug("Launching browser for form filling")
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=False)  # Visible browser for debugging
                page = browser.new_page()
                try:
                    # Load the job application page
                    logger.debug(f"Navigating to job URL: {payload.job_url}")
                    page.goto(payload.job_url, timeout=60000)
                    page.wait_for_timeout(3000)  # Wait for page to fully load

                    # Use form executor to fill all mapped fields
                    logger.debug("Filling form fields")
                    field_results = fill_fields(page, selector_map, data, resume_path)

                    # Take screenshot for verification
                    logger.debug(f"Taking verification screenshot: {screenshot_path}")
                    page.screenshot(path=screenshot_path)
                    
                    logger.info("Intelligent apply completed successfully")
                    return {
                        "status": "success",
                        "fields": field_results,
                        "screenshot": screenshot_path
                    }
                except Exception as e:
                    logger.error(f"Error during intelligent apply: {str(e)}")
                    # Take error screenshot for debugging
                    page.screenshot(path="uploads/intelligent_error.png")
                    return {"status": "error", "error": str(e)}
                finally:
                    browser.close()
            except Exception as e:
                logger.error(f"Error launching browser: {str(e)}")
                return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Error in intelligent apply process: {str(e)}")
        return {"status": "error", "error": str(e)}

# === NOTION LOGGING ENDPOINTS ===

class NotionLogRequest(BaseModel):
    """
    Request model for manual Notion logging
    
    Allows clients to create custom log entries in Notion
    """
    content: str    # Content for the Notion page

@router.post("/log")
@debug_performance
def log_to_notion_route(payload: NotionLogRequest):
    """Create a manual log entry in Notion."""
    logger.info("Processing manual Notion log request")
    try:
        result = log_to_notion(payload.content)
        logger.info("Successfully created Notion log entry")
        return result
    except Exception as e:
        logger.error(f"Error creating Notion log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log/auto")
@debug_performance
def auto_log_to_notion_route():
    """Create an automatic project update log in Notion."""
    logger.info("Processing automatic Notion log request")
    try:
        result = auto_log_project_update()
        logger.info("Successfully created automatic Notion log entry")
        return result
    except Exception as e:
        logger.error(f"Error creating automatic Notion log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

