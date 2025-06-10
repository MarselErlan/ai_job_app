# File: app/tasks/pipeline.py
"""
MAIN AI JOB APPLICATION PIPELINE

This is the heart of the AI job application system. It orchestrates the entire process 
from resume parsing to job application submission. The pipeline follows these steps:

1. Parse resume PDF and create AI embeddings
2. Search for jobs using Google Custom Search
3. Match resume to jobs using semantic similarity
4. Tailor resume using GPT for the best job match
5. Generate a new PDF of the tailored resume
6. Map form fields of the job application using AI
7. Auto-fill the job application form using browser automation
8. Log the entire process to Notion for tracking

Data Flow:
PDF Resume → Text → Embeddings → Job Matching → Tailored Resume → PDF → Form Filling → Notion Logging
"""

import os
import json
import re
from datetime import datetime
from loguru import logger
from app.services.resume_parser import extract_text_from_resume, embed_resume_text
from app.services.job_scraper import scrape_google_jobs
from app.services.jd_matcher import rank_job_matches
from app.services.resume_tailor import tailor_resume
from app.services.pdf_generator import save_resume_as_pdf
from app.services.field_mapper import extract_form_selectors
from app.services.form_autofiller import apply_to_ashby_job, apply_with_selector_map
from app.services.notion_logger import log_to_notion
from app.services.log_formatter import format_daily_log

def run_pipeline(
    file_path: str = None,
    name: str = "Eric Abram",
    email: str = "ericabram33@gmail.com",
    phone: str = "312-805-9851",
    role: str = "SDET",
    location: str = "Chicago"
):
    try:
        if not file_path:
            file_path = "uploads/latest_resume.pdf"
        logger.info(f"🚀 Starting pipeline for resume: {file_path}")

        if not os.path.exists(file_path):
            return {"status": "error", "message": f"Resume file not found: {file_path}"}

        logger.info("✅ Step 1: Resume parsed and embedded")
        raw_text = extract_text_from_resume(file_path)
        embedding = embed_resume_text(raw_text)

        logger.info(f"🔍 Searching jobs with keyword '{role}' in '{location}'")
        jobs = scrape_google_jobs(query=role, location=location)
        if not jobs:
            return {"status": "error", "message": "No jobs found from search."}

        ranked = rank_job_matches(jobs, embedding)
        best = ranked[0] if ranked else None
        if not best:
            return {"status": "error", "message": "No matching jobs found."}
        logger.info(f"🏆 Best match: {best['title']} ({best['url']})")

        logger.info("🧐 GPT tailoring resume")
        tailored_resume = tailor_resume(raw_text, best['snippet'])

        name_part = name.replace(' ', '_')
        filename = f"{name_part}_for_SDET_at_Company.pdf"
        pdf_path = save_resume_as_pdf(tailored_resume, filename)
        logger.info(f"📝 Tailored resume PDF saved: {pdf_path}")

        logger.info(f"💩 Extracting form selectors for: {best['url']}")
        selector_result = extract_form_selectors(best['url'])
        if selector_result.get("status") != "success":
            return {"status": "error", "message": "Field mapping failed.", "details": selector_result}

        try:
            selector_map_text = selector_result["selector_map"]
            match = re.search(r"```json\n(.*?)```", selector_map_text, re.DOTALL)
            if match:
                selector_map = json.loads(match.group(1))
            else:
                selector_map = json.loads(selector_map_text)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse selector map: {str(e)}")
            return {"status": "error", "message": f"Failed to parse selector map: {str(e)}"}

        logger.info("🧰 Attempting to fill the application form")
        try:
            apply_result = apply_with_selector_map(best['url'], selector_map, name, email, phone, pdf_path)
        except Exception as e:
            logger.warning(f"Intelligent fill failed. Falling back to Ashby method: {e}")
            apply_result = apply_to_ashby_job(best['url'], name, email, phone, pdf_path)

        if apply_result.get("status") != "success":
            return {"status": "error", "message": "Form auto-fill failed.", "details": apply_result}

        screenshot_path = apply_result.get("screenshot", "uploads/apply_screenshot.png")
        logger.info(f"📸 Screenshot saved at: {screenshot_path}")

        logger.info("📂 Logging to Notion")
        log_result = log_to_notion(
            title=f"Pipeline: AI Job Application {datetime.now().strftime('%Y-%m-%d')}",
            content=format_daily_log(
                highlights=[
                    "✅ Resume parsed & embedded",
                    "✅ Jobs scraped & matched",
                    "✅ Resume tailored via GPT",
                    "✅ PDF generated",
                    "✅ Selector map extracted via LLM",
                    "✅ Form fields filled with Playwright"
                ],
                changed_files=[
                    "pipeline.py",
                    "resume_parser.py",
                    "job_scraper.py",
                    "jd_matcher.py",
                    "resume_tailor.py",
                    "pdf_generator.py",
                    "field_mapper.py",
                    "form_autofiller.py"
                ],
                screenshot=screenshot_path
            )
        )

        logger.success("🌟 Pipeline completed successfully")
        return {
            "status": "success",
            "message": "Pipeline completed successfully",
            "best_job": {
                "title": best.get("title"),
                "url": best.get("url"),
                "score": best.get("score")
            },
            "tailored_resume": tailored_resume,
            "pdf_path": pdf_path,
            "screenshot": screenshot_path,
            "notion_log": log_result
        }

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Pipeline failed with exception: {str(e)}"
        }
