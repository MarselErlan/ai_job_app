# File: app/tasks/pipeline.py
"""
MAIN AI JOB APPLICATION PIPELINE

This is the heart of the AI job application system. It orchestrates the entire process 
from resume parsing to job application submission. The pipeline follows these steps:

1. Parse resume PDF and create AI embeddings
2. Search for jobs using Google Custom Search with multiple strategies
3. Match resume to jobs using semantic similarity
4. Check database to skip already processed jobs
5. Keep searching until new jobs are found or max attempts reached
6. Tailor resume using GPT for the best job match
7. Generate a new PDF of the tailored resume
8. Map form fields of the job application using AI
9. Auto-fill the job application form using browser automation
10. Save job to database and log the entire process to Notion

Data Flow:
PDF Resume → Text → Embeddings → Persistent Job Search → DB Check → Tailored Resume → PDF → Form Filling → DB Save → Notion Logging
"""

import os
import json
import re
import time
from datetime import datetime
from loguru import logger
from app.services.resume_parser import extract_text_from_resume, embed_resume_text
from app.services.enhanced_job_scraper import scrape_google_jobs, scrape_google_jobs_enhanced
from app.services.jd_matcher import rank_job_matches
from app.services.resume_tailor import tailor_resume
from app.services.pdf_generator import save_resume_as_pdf
from app.services.field_mapper import extract_form_selectors
from app.services.form_autofiller import apply_to_ashby_job, apply_with_selector_map
from app.services.notion_logger import log_to_notion
from app.services.log_formatter import format_daily_log
from app.db.session import SessionLocal
from app.db.crud import job_exists, create_job_entry, get_all_job_urls
from app.utils.debug_utils import (
    debug_performance, debug_memory, debug_section, 
    debug_log_object, create_debug_checkpoint
)

@debug_performance
def generate_search_variations(role: str, location: str) -> list[dict]:
    """
    🔄 GENERATE MULTIPLE SEARCH STRATEGIES FOR BETTER JOB DISCOVERY
    
    This function creates different search variations to maximize the chances
    of finding new job opportunities. It tries different keywords, locations,
    and search approaches to cast a wider net.
    
    Args: 
        role (str): Primary job role (e.g., "SDET")
        location (str): Primary location (e.g., "Chicago")
        
    Returns:
        list[dict]: List of search strategies to try
    """
    
    debug_memory("Start generate_search_variations")
    logger.debug(f"🔄 Generating search variations for role='{role}', location='{location}'")
    
    # Create variations based on role
    role_variations = []
    
    if "SDET" in role.upper():
        role_variations = [
            "SDET",
            "Software Development Engineer in Test", 
            "Test Automation Engineer",
            "QA Automation Engineer",
            "Software Test Engineer",
            "Automation QA",
            "Test Engineer Python",
            "QA Engineer Selenium"
        ]
    elif "SOFTWARE ENGINEER" in role.upper():
        role_variations = [
            "Software Engineer",
            "Software Developer", 
            "Backend Engineer",
            "Full Stack Engineer",
            "Python Developer",
            "Web Developer"
        ]
    else:
        # Default variations for any role
        role_variations = [
            role,
            f"{role} Engineer",
            f"Senior {role}",
            f"{role} Developer"
        ]
    
    logger.debug(f"📝 Generated {len(role_variations)} role variations")
    
    # Create location variations
    location_variations = [location]
    if location.lower() != "remote":
        location_variations.extend([
            "Remote",
            f"{location} Remote",
            f"Remote {location}"
        ])
    
    logger.debug(f"📍 Generated {len(location_variations)} location variations")
    
    # Generate all combinations
    search_strategies = []
    for role_var in role_variations[:4]:  # Limit to first 4 role variations
        for loc_var in location_variations[:3]:  # Limit to first 3 location variations
            search_strategies.append({
                "query": role_var,
                "location": loc_var,
                "description": f"Searching for '{role_var}' in '{loc_var}'"
            })
    
    logger.debug(f"🎯 Generated {len(search_strategies)} total search strategies")
    debug_memory("End generate_search_variations")
    return search_strategies

@debug_performance
def persistent_job_search(role: str, location: str, existing_urls: set, max_attempts: int = 10) -> tuple[list, dict]:
    """
    🎯 PERSISTENT JOB SEARCH WITH MULTIPLE STRATEGIES
    
    This function keeps searching for jobs using different strategies until it finds
    new opportunities or reaches the maximum number of attempts. It's designed to
    be thorough and not give up easily.
    
    Search Strategy:
    1. Try different role keywords (SDET, Test Automation Engineer, etc.)
    2. Try different location formats (Chicago, Remote, Chicago Remote)
    3. Combine role and location variations
    4. Filter out existing URLs after each search
    5. Stop when new jobs are found or max attempts reached
    
    Args:
        role (str): Job role to search for
        location (str): Geographic location
        existing_urls (set): URLs already in database
        max_attempts (int): Maximum search attempts before giving up
        
    Returns:
        tuple[list, dict]: (new_jobs_found, search_statistics)
    """
    
    checkpoint_id = create_debug_checkpoint()
    debug_memory("Start persistent_job_search")
    
    logger.info(f"🔍 Starting persistent job search for '{role}' in '{location}'")
    logger.debug(f"🎯 Max attempts: {max_attempts}, Existing URLs: {len(existing_urls)}")
    
    with debug_section("Generate search strategies"):
        search_strategies = generate_search_variations(role, location)
    
    all_found_jobs = []
    new_jobs = []
    search_stats = {
        "total_attempts": 0,
        "strategies_tried": [],
        "total_jobs_found": 0,
        "new_jobs_found": 0,
        "duplicate_jobs_skipped": 0,
        "checkpoint_id": checkpoint_id
    }
    
    for attempt, strategy in enumerate(search_strategies[:max_attempts], 1):
        logger.info(f"🔍 Attempt {attempt}/{min(len(search_strategies), max_attempts)}: {strategy['description']}")
        
        with debug_section(f"Search attempt {attempt}"):
            try:
                debug_memory(f"Before search attempt {attempt}")
                
                # Search with current strategy using enhanced scraper
                if attempt == 1:  # Use enhanced scraper for first attempt
                    logger.info("🚀 Using enhanced job scraper with LangChain integration")
                    jobs = scrape_google_jobs_enhanced(
                        query=strategy["query"], 
                        location=strategy["location"],
                        num_results=25  # Get more results with enhanced scraper
                    )
                else:
                    # Use standard scraper for subsequent attempts
                    jobs = scrape_google_jobs(
                        query=strategy["query"], 
                        location=strategy["location"],
                        num_results=15
                    )
                
                search_stats["total_attempts"] = attempt
                search_stats["strategies_tried"].append(strategy["description"])
                
                if jobs:
                    logger.info(f"📋 Found {len(jobs)} jobs from search")
                    logger.debug(f"📊 Jobs found: {[job.get('title', 'Unknown')[:50] for job in jobs[:3]]}...")
                    search_stats["total_jobs_found"] += len(jobs)
                    all_found_jobs.extend(jobs)
                    
                    # Filter for new jobs
                    strategy_new_jobs = []
                    for job in jobs:
                        job_url = job.get("url", "")
                        if job_url and job_url not in existing_urls:
                            # Check if we already found this job in a previous attempt
                            if not any(existing_job.get("url") == job_url for existing_job in new_jobs):
                                strategy_new_jobs.append(job)
                                new_jobs.append(job)
                                logger.debug(f"✨ New job: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                        else:
                            search_stats["duplicate_jobs_skipped"] += 1
                            logger.debug(f"⏭️ Skipping existing: {job.get('title', 'Unknown')}")
                    
                    if strategy_new_jobs:
                        logger.info(f"🎯 Found {len(strategy_new_jobs)} new jobs with this strategy")
                        debug_log_object(strategy_new_jobs[0], "First new job found")
                    else:
                        logger.info(f"⏭️ No new jobs found with this strategy (all {len(jobs)} already processed)")
                    
                    # If we found enough new jobs, we can stop searching
                    if len(new_jobs) >= 5:  # Stop after finding 5 new jobs
                        logger.info(f"🎉 Found sufficient new jobs ({len(new_jobs)}), stopping search")
                        break
                        
                else:
                    logger.warning(f"❌ No jobs found with strategy: {strategy['description']}")
                
                debug_memory(f"After search attempt {attempt}")
                
                # Small delay between searches to be respectful to APIs
                if attempt < min(len(search_strategies), max_attempts):
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"❌ Search attempt {attempt} failed: {e}")
                continue
    
    search_stats["new_jobs_found"] = len(new_jobs)
    
    # Log final search results
    if new_jobs:
        logger.success(f"✅ Persistent search completed: Found {len(new_jobs)} new jobs after {search_stats['total_attempts']} attempts")
        debug_log_object(search_stats, "Final search statistics")
    else:
        logger.warning(f"⚠️ No new jobs found after {search_stats['total_attempts']} search attempts")
    
    debug_memory("End persistent_job_search")
    return new_jobs, search_stats

@debug_performance
def run_pipeline(
    file_path: str = None,
    name: str = "Eric Abram",
    email: str = "ericabram33@gmail.com",
    phone: str = "312-805-9851",
    role: str = "SDET",
    location: str = "Chicago"
):
    """
    🚀 MAIN PIPELINE EXECUTION WITH PERSISTENT JOB SEARCH
    
    This function runs the complete job application pipeline with intelligent
    persistent searching that keeps trying different strategies until it finds
    new job opportunities or reaches maximum attempts.
    
    Enhanced Features:
    - Multiple search strategies (different keywords, locations)
    - Persistent searching until new jobs are found
    - Efficient database checking to avoid duplicates
    - Detailed statistics and logging
    - Graceful handling of search failures
    
    Args:
        file_path (str): Path to resume PDF file
        name (str): Applicant's full name
        email (str): Applicant's email address
        phone (str): Applicant's phone number
        role (str): Job role to search for (e.g., "SDET", "Software Engineer")
        location (str): Geographic location for job search
        
    Returns:
        dict: Pipeline execution results with detailed status and statistics
    """
    
    pipeline_checkpoint = create_debug_checkpoint()
    debug_memory("Pipeline start")
    
    logger.info(f"🚀 Starting pipeline execution with checkpoint: {pipeline_checkpoint}")
    debug_log_object({
        "file_path": file_path,
        "name": name,
        "email": email,
        "phone": phone,
        "role": role,
        "location": location
    }, "Pipeline parameters")
    
    # Initialize database session with proper cleanup
    db = SessionLocal()
    
    try:
        with debug_section("Resume validation"):
            # === STEP 1: RESUME VALIDATION ===
            if not file_path:
                file_path = "uploads/latest_resume.pdf"
            logger.info(f"🚀 Starting pipeline for resume: {file_path}")

            if not os.path.exists(file_path):
                return {"status": "error", "message": f"Resume file not found: {file_path}"}

        with debug_section("Resume processing"):
            # === STEP 2: RESUME PROCESSING ===
            logger.info("📄 Step 1: Parsing resume and creating embeddings")
            debug_memory("Before resume parsing")
            
            raw_text = extract_text_from_resume(file_path)
            logger.debug(f"📝 Extracted text length: {len(raw_text)} characters")
            
            embedding = embed_resume_text(raw_text)
            logger.debug(f"🧠 Embedding dimensions: {len(embedding) if embedding else 'None'}")
            
            debug_memory("After resume processing")
            logger.info("✅ Resume parsed and embedded successfully")

        with debug_section("Database preparation"):
            # === STEP 3: DATABASE PREPARATION ===
            logger.info("🗄️ Step 2: Getting existing job URLs from database")
            existing_urls = get_all_job_urls(db)
            logger.info(f"📊 Found {len(existing_urls)} existing job URLs in database")
            debug_log_object(list(existing_urls)[:5], "Sample existing URLs")

        with debug_section("Persistent job search"):
            # === STEP 4: PERSISTENT JOB SEARCH ===
            logger.info(f"🔍 Step 3: Starting persistent job search for '{role}' in '{location}'")
            new_jobs, search_stats = persistent_job_search(
                role=role, 
                location=location, 
                existing_urls=existing_urls,
                max_attempts=10
            )
        
        # Check if we found any new jobs
        if not new_jobs:
            return {
                "status": "no_new_jobs",
                "message": f"No new jobs found after {search_stats['total_attempts']} search attempts with different strategies.",
                "search_stats": search_stats,
                "suggestions": [
                    "Try running again later as new jobs get posted regularly",
                    "Consider expanding your search to nearby cities",
                    "Try different role variations in your search",
                    "Check if your database has too many existing jobs for this role/location"
                ],
                "checkpoint_id": pipeline_checkpoint
            }

        logger.info(f"🎯 Found {len(new_jobs)} new jobs after persistent search")

        with debug_section("Job matching"):
            # === STEP 5: INTELLIGENT JOB MATCHING ===
            logger.info("🧠 Step 4: Ranking new jobs by resume compatibility")
            debug_memory("Before job ranking")
            
            ranked_new_jobs = rank_job_matches(new_jobs, embedding)
            
            if not ranked_new_jobs:
                return {"status": "error", "message": "No matching jobs found after ranking."}

            # Select the best matching new job
            best_job = ranked_new_jobs[0]
            logger.info(f"🏆 Best new job match: {best_job.get('title', 'Unknown')} (Score: {best_job.get('score', 0):.3f})")
            logger.info(f"🔗 Company: {best_job.get('company', 'Unknown')}")
            logger.info(f"🔗 Job URL: {best_job.get('url', 'Unknown')}")
            debug_log_object(best_job, "Best job match")
            
            debug_memory("After job ranking")

        with debug_section("Race condition check"):
            # === STEP 6: FINAL DATABASE CHECK (RACE CONDITION PROTECTION) ===
            if job_exists(db, best_job.get('url', '')):
                logger.warning(f"⚠️ Race condition detected: Job was added to DB during processing")
                return {
                    "status": "race_condition", 
                    "message": "Job was processed by another instance during execution.",
                    "job_url": best_job.get('url', ''),
                    "checkpoint_id": pipeline_checkpoint
                }

        with debug_section("Resume tailoring"):
            # === STEP 7: RESUME TAILORING ===
            logger.info("✏️ Step 5: Tailoring resume with GPT-4 for specific job")
            debug_memory("Before resume tailoring")
            
            tailored_resume = tailor_resume(raw_text, best_job.get('snippet', ''))
            logger.debug(f"📄 Tailored resume length: {len(tailored_resume)} characters")
            
            debug_memory("After resume tailoring")
            logger.info("✅ Resume tailored successfully")

        with debug_section("PDF generation"):
            # === STEP 8: PDF GENERATION ===
            logger.info("📄 Step 6: Generating tailored resume PDF")
            debug_memory("Before PDF generation")
            
            name_part = name.replace(' ', '_')
            company_name = best_job.get('company', 'Company')
            filename = f"{name_part}_for_{role}_at_{company_name.replace(' ', '_')}.pdf"
            pdf_path = save_resume_as_pdf(tailored_resume, filename)
            logger.info(f"📝 Tailored resume PDF saved: {pdf_path}")
            
            debug_memory("After PDF generation")

        with debug_section("Form field mapping"):
            # === STEP 9: FORM FIELD MAPPING ===
            logger.info(f"🗺️ Step 7: Mapping form fields for: {best_job.get('url', '')}")
            debug_memory("Before form mapping")
            
            # Check if this is a fallback/mock job (which won't have real forms)
            is_fallback_job = best_job.get('source') == 'Fallback (Quota Exceeded)'
            
            if is_fallback_job:
                logger.warning("⚠️ Detected fallback job - skipping real form mapping and using mock selectors")
                # Create a mock selector map for fallback jobs
                selector_result = {
                    "status": "success",
                    "selector_map": """{
    "full_name": "input[name='name'], input[data-testid='Field-name']",
    "email": "input[name='email'], input[data-testid='Field-email']",
    "phone": "input[name='phone'], input[data-testid='Field-phone']",
    "resume_upload": "input[type='file']"
}"""
                }
                logger.info("✅ Using mock selector map for fallback job")
            else:
                # Real job - attempt form mapping
                selector_result = extract_form_selectors(best_job.get('url', ''))
                
                # Enhanced error handling for form mapping failures
                if selector_result.get("status") != "success":
                    logger.error(f"❌ Form mapping failed: {selector_result}")
                    
                    # Check if the error might be due to URL access issues
                    error_msg = selector_result.get("error", "").lower()
                    if any(keyword in error_msg for keyword in ["timeout", "net::", "404", "403", "connection"]):
                        logger.warning("⚠️ URL access error detected - treating as fallback job")
                        # Use fallback selectors for inaccessible URLs
                        selector_result = {
                            "status": "success",
                            "selector_map": """{
    "full_name": "input[name='name'], input[data-testid='Field-name']",
    "email": "input[name='email'], input[data-testid='Field-email']", 
    "phone": "input[name='phone'], input[data-testid='Field-phone']",
    "resume_upload": "input[type='file']"
}"""
                        }
                        logger.info("✅ Using fallback selector map due to URL access issues")
                    else:
                        return {"status": "error", "message": "Field mapping failed.", "details": selector_result}
            
            debug_memory("After form mapping")

        with debug_section("JSON parsing"):
            # === STEP 10: JSON PARSING ===
            logger.info("📝 Step 8: Parsing AI-generated form selectors")
            try:
                # Enhanced validation before JSON parsing
                if "selector_map" not in selector_result:
                    raise KeyError("selector_map key missing from result")
                
                selector_map_text = selector_result["selector_map"]
                
                if not selector_map_text or selector_map_text.strip() == "":
                    raise ValueError("selector_map is empty")
                
                # Try to parse JSON with markdown code block extraction
                match = re.search(r"```json\n(.*?)```", selector_map_text, re.DOTALL)
                if match:
                    selector_map = json.loads(match.group(1))
                    logger.debug("✅ Parsed JSON from markdown code block")
                else:
                    # Try direct JSON parsing
                    selector_map = json.loads(selector_map_text)
                    logger.debug("✅ Parsed JSON directly")
                
                logger.info(f"✅ Successfully parsed {len(selector_map)} form selectors")
                debug_log_object(selector_map, "Parsed selector map")
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(f"❌ Failed to parse selector map: {str(e)}")
                logger.error(f"🔍 Problematic selector_map content: {selector_result.get('selector_map', 'MISSING')}")
                
                # Provide emergency fallback selectors
                logger.warning("⚠️ Using emergency fallback selectors")
                selector_map = {
                    "full_name": "input[name='name']",
                    "email": "input[name='email']", 
                    "phone": "input[name='phone']",
                    "resume_upload": "input[type='file']"
                }
                logger.info(f"✅ Emergency fallback: Using {len(selector_map)} basic selectors")

        with debug_section("Form filling"):
            # === STEP 11: AUTOMATED FORM FILLING ===
            logger.info("🤖 Step 9: Attempting automated form filling")
            debug_memory("Before form filling")
            
            try:
                # Try intelligent form filling first
                apply_result = apply_with_selector_map(
                    best_job.get('url', ''), selector_map, name, email, phone, pdf_path
                )
                logger.info("✅ Intelligent form filling completed")
            except Exception as e:
                logger.warning(f"⚠️ Intelligent filling failed, falling back to Ashby method: {e}")
                # Fallback to Ashby-specific selectors
                apply_result = apply_to_ashby_job(
                    best_job.get('url', ''), name, email, phone, pdf_path
                )

            if apply_result.get("status") != "success":
                logger.error(f"❌ Form filling failed: {apply_result}")
                return {"status": "error", "message": "Form auto-fill failed.", "details": apply_result}

            screenshot_path = apply_result.get("screenshot", "uploads/apply_screenshot.png")
            logger.info(f"📸 Application screenshot saved: {screenshot_path}")
            
            debug_memory("After form filling")

        with debug_section("Database save"):
            # === STEP 12: DATABASE SAVE ===
            logger.info("💾 Step 10: Saving job application to database")
            debug_memory("Before database save")
            
            try:
                job_entry = create_job_entry(db, {
                    "title": best_job.get("title"),
                    "url": best_job.get("url"),
                    "company_name": best_job.get("company"),
                    "location": location,
                    "resume_used": pdf_path,
                    "screenshot_path": screenshot_path,
                    "applied": True,
                    "status": "applied",
                    "notes": f"Auto-applied via pipeline. Match score: {best_job.get('score', 0):.3f}. Found after {search_stats['total_attempts']} search attempts. Checkpoint: {pipeline_checkpoint}"
                })
                logger.info(f"✅ Job saved to database with ID: {job_entry.id}")
                debug_memory("After database save")
            except Exception as e:
                logger.error(f"❌ Failed to save job to database: {e}")
                # Continue with Notion logging even if DB save fails

        with debug_section("Notion logging"):
            # === STEP 13: NOTION LOGGING ===
            logger.info("📝 Step 11: Creating Notion documentation")
            debug_memory("Before Notion logging")
            
            log_result = log_to_notion(
                title=f"🎯 Applied: {best_job.get('title', 'Unknown')} at {best_job.get('company', 'Unknown')}",
                content=format_daily_log(
                    highlights=[
                        "✅ Resume parsed & embedded",
                        f"✅ Persistent search: {search_stats['total_attempts']} attempts, {len(new_jobs)} new jobs found",
                        f"✅ Best match: {best_job.get('title', 'Unknown')} (Score: {best_job.get('score', 0):.3f})",
                        "✅ Resume tailored via GPT-4",
                        "✅ PDF generated with company name",
                        "✅ Form selectors mapped via AI",
                        "✅ Application submitted successfully",
                        "✅ Job saved to database",
                        f"✅ Debug checkpoint: {pipeline_checkpoint}"
                    ],
                    changed_files=[
                        "pipeline.py",
                        "resume_parser.py",
                        "job_scraper.py",
                        "jd_matcher.py",
                        "resume_tailor.py",
                        "pdf_generator.py",
                        "field_mapper.py",
                        "form_autofiller.py",
                        "crud.py",
                        "debug_utils.py"
                    ],
                    screenshot=screenshot_path
                )
            )
            
            debug_memory("After Notion logging")

        logger.success("🌟 Pipeline completed successfully!")
        debug_memory("Pipeline end")

        return {
            "status": "success",
            "message": "Pipeline completed successfully with persistent job search",
            "checkpoint_id": pipeline_checkpoint,
            "search_stats": search_stats,
            "job_discovery": {
                "existing_jobs_in_db": len(existing_urls),
                "new_jobs_found": len(new_jobs),
                "search_attempts": search_stats['total_attempts'],
                "strategies_tried": search_stats['strategies_tried']
            },
            "best_job": {
                "title": best_job.get("title"),
                "url": best_job.get("url"),
                "company": best_job.get("company"),
                "score": best_job.get("score")
            },
            "tailored_resume": tailored_resume,
            "pdf_path": pdf_path,
            "screenshot": screenshot_path,
            "notion_log": log_result,
            "database_id": getattr(job_entry, 'id', None) if 'job_entry' in locals() else None
        }

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}", exc_info=True)
        debug_memory("Pipeline error")
        return {
            "status": "error", 
            "message": f"Pipeline failed with exception: {str(e)}",
            "checkpoint_id": pipeline_checkpoint
        }
    
    finally:
        # Always close the database session
        db.close()
        logger.info("🔒 Database session closed")
        debug_memory("Pipeline cleanup complete")
    