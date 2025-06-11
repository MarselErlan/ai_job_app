# File: app/services/form_autofiller.py

from playwright.sync_api import sync_playwright
import time
import os
import json
import re
from loguru import logger
from app.utils.debug_utils import debug_performance

# Configure Loguru for this module
logger.add(
    "logs/form_autofiller.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

@debug_performance
def apply_to_ashby_job(url: str, name: str, email: str, phone: str, resume_path: str) -> dict:
    """Apply to a job using Ashby-specific selectors"""
    logger.info(f"Starting Ashby job application process for URL: {url}")
    screenshot_path = "uploads/apply_screenshot.png"
    
    with sync_playwright() as p:
        logger.debug("Launching browser")
        browser = p.chromium.launch(headless=False)  # Set to True if you don't want UI
        page = browser.new_page()

        try:
            logger.debug(f"Navigating to {url}")
            page.goto(url, timeout=60000)
            page.wait_for_timeout(3000)

            # Fill form fields using Ashby-specific selectors
            try:
                logger.debug("Attempting to fill name field")
                page.wait_for_selector('input[data-testid="Field-name"]', timeout=10000)
                page.fill('input[data-testid="Field-name"]', name)
                logger.debug("Successfully filled name field")
            except Exception as e:
                logger.warning(f"Primary name selector failed: {e}")
                # Try alternative name selectors
                try:
                    page.fill('input[name="name"]', name)
                    logger.debug("Successfully filled name using fallback selector")
                except Exception as e2:
                    logger.warning(f"Secondary name selector failed: {e2}")
                    page.fill('input[placeholder*="name" i]', name)
                    logger.debug("Successfully filled name using final fallback selector")

            try:
                logger.debug("Attempting to fill email field")
                page.wait_for_selector('input[data-testid="Field-email"]', timeout=10000)
                page.fill('input[data-testid="Field-email"]', email)
                logger.debug("Successfully filled email field")
            except Exception as e:
                logger.warning(f"Primary email selector failed: {e}")
                # Try alternative email selectors
                try:
                    page.fill('input[name="email"]', email)
                    logger.debug("Successfully filled email using fallback selector")
                except Exception as e2:
                    logger.warning(f"Secondary email selector failed: {e2}")
                    page.fill('input[type="email"]', email)
                    logger.debug("Successfully filled email using final fallback selector")

            try:
                logger.debug("Attempting to fill phone field")
                page.wait_for_selector('input[data-testid="Field-phone"]', timeout=10000)
                page.fill('input[data-testid="Field-phone"]', phone)
                logger.debug("Successfully filled phone field")
            except Exception as e:
                logger.warning(f"Primary phone selector failed: {e}")
                # Try alternative phone selectors
                try:
                    page.fill('input[name="phone"]', phone)
                    logger.debug("Successfully filled phone using fallback selector")
                except Exception as e2:
                    logger.warning(f"Secondary phone selector failed: {e2}")
                    page.fill('input[placeholder*="phone" i]', phone)
                    logger.debug("Successfully filled phone using final fallback selector")

            # Upload resume
            try:
                logger.debug(f"Attempting to upload resume from {resume_path}")
                page.wait_for_selector('input[type="file"]', timeout=10000)
                page.set_input_files('input[type="file"]', resume_path)
                page.wait_for_timeout(2000)
                logger.info("Resume uploaded successfully")
            except Exception as e:
                logger.error(f"Resume upload failed: {e}")

            # Submit form (optional - you might want to review before submitting)
            try:
                logger.debug("Attempting to submit form")
                page.click('button[type="submit"]')
                page.wait_for_timeout(3000)
                logger.info("Form submitted successfully")
            except Exception as e:
                logger.warning(f"Submit failed (this might be expected): {e}")

            # Save screenshot after submission
            logger.debug(f"Saving submission screenshot to {screenshot_path}")
            page.screenshot(path=screenshot_path)

            browser.close()
            logger.info("Application process completed successfully")
            return {"status": "success", "screenshot": screenshot_path}

        except Exception as e:
            logger.error(f"Application process failed: {str(e)}")
            error_screenshot = "uploads/error_debug.png"
            logger.debug(f"Saving error screenshot to {error_screenshot}")
            page.screenshot(path=error_screenshot)
            browser.close()
            return {"status": "error", "error": str(e)}

@debug_performance
def apply_with_selector_map(url: str, selector_map: dict, name: str, email: str, phone: str, resume_path: str) -> dict:
    """Apply to a job using dynamically mapped selectors"""
    logger.info(f"Starting dynamic form application process for URL: {url}")
    screenshot_path = "uploads/intelligent_apply.png"
    
    with sync_playwright() as p:
        logger.debug("Launching browser")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            logger.debug(f"Navigating to {url}")
            page.goto(url, timeout=60000)
            page.wait_for_timeout(3000)

            # Prepare data mapping
            data = {
                "full_name": name,
                "name": name,
                "_systemfield_name": name,
                "email": email,
                "_systemfield_email": email,
                "phone": phone,
                "_systemfield_phone": phone
            }

            field_results = {}
            logger.debug(f"Using selector map: {selector_map}")

            # Fill form fields using the selector map
            for field_key, selector in selector_map.items():
                logger.debug(f"Processing field: {field_key} with selector: {selector}")
                
                if field_key in ["resume_upload", "_systemfield_resume", "resume"] and resume_path:
                    try:
                        page.set_input_files(selector, resume_path)
                        field_results[field_key] = "uploaded"
                        logger.debug(f"Successfully uploaded resume for {field_key}")
                    except Exception as e:
                        error_msg = f"upload error: {str(e)}"
                        field_results[field_key] = error_msg
                        logger.error(f"Failed to upload resume for {field_key}: {error_msg}")
                elif field_key in data:
                    try:
                        page.fill(selector, data[field_key])
                        field_results[field_key] = "filled"
                        logger.debug(f"Successfully filled {field_key}")
                    except Exception as e:
                        error_msg = f"fill error: {str(e)}"
                        field_results[field_key] = error_msg
                        logger.error(f"Failed to fill {field_key}: {error_msg}")
                else:
                    field_results[field_key] = "skipped (no data)"
                    logger.warning(f"Skipped {field_key} - no data available")

            # Take screenshot before submitting
            logger.debug(f"Saving application screenshot to {screenshot_path}")
            page.screenshot(path=screenshot_path)

            browser.close()
            logger.info("Dynamic form application completed successfully")
            return {
                "status": "success",
                "fields": field_results,
                "screenshot": screenshot_path
            }

        except Exception as e:
            logger.error(f"Dynamic form application failed: {str(e)}")
            error_screenshot = "uploads/intelligent_error.png"
            logger.debug(f"Saving error screenshot to {error_screenshot}")
            page.screenshot(path=error_screenshot)
            browser.close()
            return {"status": "error", "error": str(e)}
