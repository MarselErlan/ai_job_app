# File: app/api/v1/resume.py

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

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

latest_embedding = None  # Global cache for current session

class ResumeTailorRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: str
    company_name: str

class AutoApplyRequest(BaseModel):
    job_url: str
    name: str
    email: str
    phone: str
    resume_filename: str

class FormMapRequest(BaseModel):
    job_url: str

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
        name_part = payload.resume_text.splitlines()[0].replace(' ', '_')
        job_part = payload.job_title.replace(' ', '_')
        company_part = payload.company_name.replace(' ', '_')
        filename = f"{name_part}_for_{job_part}_at_{company_part}.pdf"
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
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path=file_path, filename=filename, media_type='application/pdf')

@router.post("/apply")
def auto_apply(payload: AutoApplyRequest):
    resume_path = os.path.join(UPLOAD_DIR, payload.resume_filename)
    if not os.path.exists(resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found.")

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
        result = extract_form_selectors(payload.job_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply/intelligent")
def apply_intelligent(payload: AutoApplyRequest):
    resume_path = os.path.join(UPLOAD_DIR, payload.resume_filename)
    if not os.path.exists(resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found.")

    # Get selector map from LLM
    map_result = extract_form_selectors(payload.job_url)
    if map_result["status"] != "success":
        return map_result

    import re, json
    match = re.search(r"```json\n(.*?)```", map_result["selector_map"], re.DOTALL)
    if match:
        selector_map = json.loads(match.group(1))
    else:
        raise HTTPException(status_code=500, detail="Could not extract valid JSON selector map.")  # Convert from string JSON
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

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto(payload.job_url, timeout=60000)
            page.wait_for_timeout(3000)

            field_results = fill_fields(page, selector_map, data, resume_path)

            page.screenshot(path=screenshot_path)
            return {
                "status": "success",
                "fields": field_results,
                "screenshot": screenshot_path
            }
        except Exception as e:
            page.screenshot(path="uploads/intelligent_error.png")
            return {"status": "error", "error": str(e)}
        finally:
            browser.close()
