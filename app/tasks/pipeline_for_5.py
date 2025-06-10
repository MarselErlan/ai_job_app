# File: app/tasks/pipeline_for_5.py

import os
import json
import re
from loguru import logger
from sqlalchemy.orm import Session

from app.services.resume_parser import extract_text_from_resume, embed_resume_text
from app.services.job_scraper import scrape_google_jobs
from app.services.jd_matcher import rank_job_matches
from app.services.resume_tailor import tailor_resume
from app.services.pdf_generator import save_resume_as_pdf
from app.services.field_mapper import extract_form_selectors
from app.services.form_autofiller import apply_to_ashby_job, apply_with_selector_map
from app.services.notion_logger import log_to_notion
from app.services.log_formatter import format_daily_log
from app.db.session import SessionLocal
from app.db.crud import job_exists, create_job_entry


def run_pipeline_multi_apply(file_path: str, name: str, email: str, phone: str, role: str, location: str, max_jobs: int = 5):
    logger.info(f"\n🚀 Starting multi-apply pipeline with resume: {file_path}")

    if not os.path.exists(file_path):
        return {"status": "error", "message": f"Resume file not found: {file_path}"}

    db: Session = SessionLocal()

    try:
        raw_text = extract_text_from_resume(file_path)
        embedding = embed_resume_text(raw_text)

        logger.info("🔍 Searching for jobs...")
        jobs = scrape_google_jobs(query=role, location=location, num_results=10)
        ranked = rank_job_matches(jobs, embedding)

        results = []
        screenshots = []
        applied_count = 0

        for job in ranked:
            if applied_count >= max_jobs:
                break

            title = job.get("title")
            url = job.get("url")
            snippet = job.get("snippet")

            if job_exists(db, url):
                logger.info(f"⏭️ Skipping duplicate job: {title}")
                continue

            logger.info(f"\n📌 Applying to: {title} ({url})")

            try:
                tailored_resume = tailor_resume(raw_text, snippet)
                filename = f"{name.replace(' ', '_')}_for_SDET.pdf"
                pdf_path = save_resume_as_pdf(tailored_resume, filename)

                selector_result = extract_form_selectors(url)
                if selector_result.get("status") != "success":
                    raise Exception("Selector map extraction failed")

                try:
                    selector_map_text = selector_result["selector_map"]
                    match = re.search(r"```json\n(.*?)```", selector_map_text, re.DOTALL)
                    selector_map = json.loads(match.group(1)) if match else json.loads(selector_map_text)
                except Exception as e:
                    raise Exception(f"Selector map parse error: {e}")

                apply_result = apply_with_selector_map(url, selector_map, name, email, phone, pdf_path)
                if apply_result.get("status") != "success":
                    apply_result = apply_to_ashby_job(url, name, email, phone, pdf_path)

                if apply_result.get("status") == "success":
                    screenshot = apply_result.get("screenshot", "uploads/intelligent_apply.png")
                    screenshots.append(screenshot)
                    results.append(f"✅ Applied: {title} — {url}")
                    create_job_entry(db, {
                        "title": title,
                        "url": url,
                        "resume_used": pdf_path,
                        "screenshot_path": screenshot,
                        "applied": True,
                        "status": "applied"
                    })
                    logger.success(f"✅ Applied to job: {title}")
                else:
                    raise Exception(apply_result.get("error", "Unknown error"))

            except Exception as e:
                results.append(f"❌ Failed: {title} — {str(e)}")
                create_job_entry(db, {
                    "title": title,
                    "url": url,
                    "resume_used": file_path,
                    "applied": False,
                    "status": "failed"
                })
                logger.error(f"❌ Error while applying to {title}: {str(e)}")

            applied_count += 1

        notion_log = log_to_notion(
            title="Pipeline: Auto Apply 5 Jobs",
            content=format_daily_log(
                highlights=results,
                changed_files=["pipeline_for_5.py"],
                screenshot=screenshots[0] if screenshots else None
            )
        )

        return {
            "status": "success",
            "message": f"Applied to {applied_count} job(s)",
            "logs": results,
            "screenshots": screenshots,
            "notion_log": notion_log
        }

    finally:
        db.close()
