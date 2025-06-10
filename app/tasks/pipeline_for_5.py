# File: app/tasks/pipeline_for_5.py

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


def run_pipeline_multi_apply(
    file_path: str = None,
    name: str = "Eric Abram",
    email: str = "ericabram33@gmail.com",
    phone: str = "312-805-9851",
    role: str = "SDET",
    location: str = "Chicago"
):
    logger.info(f"\n\n🚀 Starting multi-apply pipeline with resume: {file_path or 'uploads/latest_resume.pdf'}")
    
    try:
        file_path = file_path or "uploads/latest_resume.pdf"
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"Resume not found: {file_path}"}

        raw_text = extract_text_from_resume(file_path)
        embedding = embed_resume_text(raw_text)

        logger.info("🔍 Searching for jobs...")
        jobs = scrape_google_jobs(query=role, location=location)
        if not jobs:
            return {"status": "error", "message": "No jobs found"}

        ranked = rank_job_matches(jobs, embedding)
        top_jobs = ranked[:5]
        logs = []
        screenshots = []

        for idx, job in enumerate(top_jobs, 1):
            logger.info(f"\n📌 [{idx}] Applying to: {job['title']} ({job['url']})")
            try:
                tailored = tailor_resume(raw_text, job['snippet'])
                filename = f"{name.replace(' ', '_')}_for_SDET_{idx}.pdf"
                pdf_path = save_resume_as_pdf(tailored, filename)

                selector_result = extract_form_selectors(job['url'])
                if selector_result.get("status") != "success":
                    raise ValueError("Selector mapping failed")

                text = selector_result["selector_map"]
                match = re.search(r"```json\n(.*?)```", text, re.DOTALL)
                selector_map = json.loads(match.group(1)) if match else json.loads(text)

                apply_result = apply_with_selector_map(job['url'], selector_map, name, email, phone, pdf_path)
                if apply_result.get("status") != "success":
                    raise RuntimeError("Form fill failed")

                screenshot = apply_result.get("screenshot")
                screenshots.append(screenshot)
                logs.append(f"✅ Applied: {job['title']} — {job['url']}")
                logger.success(f"✅ Applied to job: {job['title']}")

            except Exception as e:
                logs.append(f"❌ Failed: {job['title']} — {str(e)}")
                logger.error(f"❌ Error while applying to {job['title']}: {str(e)}")

        log_body = format_daily_log(
            highlights=["🚀 Auto-applied to 5 jobs"],
            changed_files=["pipeline.py"],
            screenshot=screenshots[-1] if screenshots else None
        )
        notion_log = log_to_notion(f"AI Job App – Multi Apply {datetime.now().strftime('%Y-%m-%d')}", log_body)

        return {
            "status": "success",
            "message": f"Applied to {len(top_jobs)} job(s)",
            "logs": logs,
            "screenshots": screenshots,
            "notion_log": notion_log
        }

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        return {"status": "error", "message": str(e)}
