# File: app/tasks/pipeline.py

import os
import json
import re
from app.services.resume_parser import extract_text_from_resume, embed_resume_text
from app.services.job_scraper import scrape_google_jobs
from app.services.jd_matcher import rank_job_matches
from app.services.resume_tailor import tailor_resume
from app.services.pdf_generator import save_resume_as_pdf
from app.services.field_mapper import extract_form_selectors
from app.services.form_autofiller import apply_to_ashby_job, apply_with_selector_map
from app.services.notion_logger import log_to_notion
from app.services.log_formatter import format_daily_log


def run_pipeline(file_path: str = None, name: str = "Eric Abram", email: str = "ericabram33@gmail.com", phone: str = "312-805-9851"):
    """
    Run the complete job application pipeline
    """
    try:
        # === Step 1: Parse Resume ===
        if not file_path:
            file_path = "uploads/latest_resume.pdf"
        
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"Resume file not found: {file_path}"}
        
        raw_text = extract_text_from_resume(file_path)
        embedding = embed_resume_text(raw_text)

        # === Step 2: Search Jobs ===
        jobs = scrape_google_jobs("SDET", "Chicago")
        
        if not jobs:
            return {"status": "error", "message": "No jobs found from search."}

        # === Step 3: Match Resume to Jobs ===
        ranked = rank_job_matches(jobs, embedding)
        best = ranked[0] if ranked else None

        if not best:
            return {"status": "error", "message": "No matching jobs found."}

        # === Step 4: Tailor Resume ===
        tailored_resume = tailor_resume(raw_text, best['snippet'])

        # === Step 5: Generate PDF ===
        # Extract name from resume or use provided name
        name_part = name.replace(' ', '_')
        filename = f"{name_part}_for_SDET_at_Company.pdf"
        pdf_path = save_resume_as_pdf(tailored_resume, filename)

        # === Step 6: Map Form Fields with LLM ===
        selector_result = extract_form_selectors(best['url'])
        if selector_result.get("status") != "success":
            return {"status": "error", "message": "Field mapping failed.", "details": selector_result}

        # Parse the JSON from the LLM response
        try:
            selector_map_text = selector_result["selector_map"]
            # Try to extract JSON from the response
            match = re.search(r"```json\n(.*?)```", selector_map_text, re.DOTALL)
            if match:
                selector_map = json.loads(match.group(1))
            else:
                # If no code block, try to parse the whole response as JSON
                selector_map = json.loads(selector_map_text)
        except (json.JSONDecodeError, KeyError) as e:
            return {"status": "error", "message": f"Failed to parse selector map: {str(e)}"}

        # === Step 7: Auto-Fill Form ===
        # Try using the intelligent form filler with selector map first
        try:
            apply_result = apply_with_selector_map(best['url'], selector_map, name, email, phone, pdf_path)
        except Exception as e:
            # Fallback to Ashby-specific form filler
            print(f"Intelligent form filling failed, falling back to Ashby method: {e}")
            apply_result = apply_to_ashby_job(best['url'], name, email, phone, pdf_path)
        
        if apply_result.get("status") != "success":
            return {"status": "error", "message": "Form auto-fill failed.", "details": apply_result}
        
        screenshot_path = apply_result.get("screenshot", "uploads/apply_screenshot.png")

        # === Step 8: Log to Notion ===
        log_result = log_to_notion(
            title="Pipeline: AI Job Application",
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
        return {
            "status": "error", 
            "message": f"Pipeline failed with exception: {str(e)}"
        }
