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
        # === STEP 1: RESUME PARSING & EMBEDDING ===
        # This section converts your PDF resume into AI-readable format
        
        # Use default resume path if none provided
        if not file_path:
            file_path = "uploads/latest_resume.pdf"
        
        # Safety check: Make sure the resume file actually exists
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"Resume file not found: {file_path}"}
        
        # Extract raw text from PDF using PyMuPDF (fitz)
        # This converts the visual PDF into machine-readable text
        raw_text = extract_text_from_resume(file_path)
        
        # Create AI embeddings (vector representation) of the resume
        # This converts text into numbers that AI can compare with job descriptions
        # The embedding is a 1536-dimensional vector that captures semantic meaning
        embedding = embed_resume_text(raw_text)

        # === STEP 2: JOB SEARCH ===
        # Search for relevant jobs using Google's Custom Search API
        
        # Query Google for SDET jobs in Chicago
        # Returns list of job postings with title, URL, and snippet
        jobs = scrape_google_jobs("SDET", "Chicago")
        
        # Safety check: Make sure we found some jobs
        if not jobs:
            return {"status": "error", "message": "No jobs found from search."}

        # === STEP 3: INTELLIGENT JOB MATCHING ===
        # Use AI to find which jobs best match your resume
        
        # Compare your resume embedding with each job description
        # Uses cosine similarity to find semantic matches (not just keyword matching)
        # Returns jobs sorted by relevance score (0-1, higher = better match)
        ranked = rank_job_matches(jobs, embedding)
        best = ranked[0] if ranked else None  # Get the best match

        # Safety check: Make sure we found matching jobs
        if not best:
            return {"status": "error", "message": "No matching jobs found."}

        # === STEP 4: AI-POWERED RESUME TAILORING ===
        # Use GPT-4 to rewrite your resume to better match the specific job
        
        # Send your resume + job description to GPT-4
        # GPT-4 rewrites your resume to emphasize relevant skills and experience
        # It keeps all your real experience but adjusts language and focus
        tailored_resume = tailor_resume(raw_text, best['snippet'])

        # === STEP 5: PDF GENERATION ===
        # Convert the tailored resume text back into a professional PDF
        
        # Create a personalized filename for the tailored resume
        name_part = name.replace(' ', '_')  # Replace spaces with underscores for filename
        filename = f"{name_part}_for_SDET_at_Company.pdf"
        
        # Generate PDF using FPDF library with proper formatting
        pdf_path = save_resume_as_pdf(tailored_resume, filename)

        # === STEP 6: INTELLIGENT FORM MAPPING ===
        # Use AI to understand the job application form structure
        
        # Load the job application page and extract its HTML
        # Send HTML to GPT-4 to identify form fields and their selectors
        # This creates a "map" of how to fill out the specific form
        selector_result = extract_form_selectors(best['url'])
        
        # Check if form mapping was successful
        if selector_result.get("status") != "success":
            return {"status": "error", "message": "Field mapping failed.", "details": selector_result}

        # Parse the JSON response from GPT-4
        # GPT-4 returns form field mappings that we need to convert to usable format
        try:
            selector_map_text = selector_result["selector_map"]
            
            # Try to extract JSON from markdown code block (common GPT response format)
            match = re.search(r"```json\n(.*?)```", selector_map_text, re.DOTALL)
            if match:
                selector_map = json.loads(match.group(1))
            else:
                # If no code block, try to parse the whole response as JSON
                selector_map = json.loads(selector_map_text)
        except (json.JSONDecodeError, KeyError) as e:
            return {"status": "error", "message": f"Failed to parse selector map: {str(e)}"}

        # === STEP 7: AUTOMATED FORM FILLING ===
        # Use browser automation to actually fill out and submit the job application
        
        # Try intelligent form filling first (uses AI-mapped selectors)
        try:
            apply_result = apply_with_selector_map(best['url'], selector_map, name, email, phone, pdf_path)
        except Exception as e:
            # If intelligent filling fails, fall back to Ashby-specific selectors
            # Ashby is a common ATS (Applicant Tracking System) with known selectors
            print(f"Intelligent form filling failed, falling back to Ashby method: {e}")
            apply_result = apply_to_ashby_job(best['url'], name, email, phone, pdf_path)
        
        # Check if form submission was successful
        if apply_result.get("status") != "success":
            return {"status": "error", "message": "Form auto-fill failed.", "details": apply_result}
        
        # Get the screenshot path for documentation
        screenshot_path = apply_result.get("screenshot", "uploads/apply_screenshot.png")

        # === STEP 8: NOTION LOGGING & DOCUMENTATION ===
        # Log the entire process to Notion for tracking and review
        
        # Create a formatted log entry with all the steps completed
        # This helps you track what happened and review applications later
        log_result = log_to_notion(
            title="Pipeline: AI Job Application",
            content=format_daily_log(
                highlights=[
                    "✅ Resume parsed & embedded",           # Step 1 completed
                    "✅ Jobs scraped & matched",             # Steps 2-3 completed  
                    "✅ Resume tailored via GPT",            # Step 4 completed
                    "✅ PDF generated",                      # Step 5 completed
                    "✅ Selector map extracted via LLM",     # Step 6 completed
                    "✅ Form fields filled with Playwright"  # Step 7 completed
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

        # === SUCCESS! RETURN ALL RESULTS ===
        # Package up all the results for the caller
        return {
            "status": "success",
            "message": "Pipeline completed successfully",
            "best_job": {
                "title": best.get("title"),        # Job title
                "url": best.get("url"),            # Application URL
                "score": best.get("score")         # Similarity score (0-1)
            },
            "tailored_resume": tailored_resume,   # The AI-tailored resume text
            "pdf_path": pdf_path,                 # Path to generated PDF
            "screenshot": screenshot_path,        # Screenshot of filled form
            "notion_log": log_result             # Notion logging results
        }

    except Exception as e:
        # If anything goes wrong anywhere in the pipeline, return error details
        return {
            "status": "error", 
            "message": f"Pipeline failed with exception: {str(e)}"
        }
