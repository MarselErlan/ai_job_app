# File: app/services/form_executor.py
"""
FORM EXECUTOR SERVICE - Handles the actual filling of form fields with data

This service takes the field mappings created by the AI field mapper and
executes the actual form filling using Playwright. It's the "hands" that
do the typing and file uploading on job application forms.

Key Features:
- Handles both text input fields and file uploads
- Provides detailed success/failure reporting for each field
- Graceful error handling for problematic fields
- Flexible data mapping for different field naming conventions
"""

from playwright.sync_api import Page
from loguru import logger
from app.utils.debug_utils import debug_performance

# Configure Loguru for this module
logger.add(
    "logs/form_executor.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

@debug_performance
def fill_fields(page: Page, selector_map: dict, data: dict, resume_path: str = None):
    """
    Fill form fields using provided selector map and data.
    
    Args:
        page (Page): Playwright page object
        selector_map (dict): Mapping of field keys to CSS selectors
        data (dict): Data to fill in the form
        resume_path (str, optional): Path to resume file for upload
        
    Returns:
        dict: Results of field filling operations
    """
    logger.info("Starting form field filling process")
    logger.debug(f"Selector map: {selector_map}")
    logger.debug(f"Data keys available: {list(data.keys())}")
    if resume_path:
        logger.debug(f"Resume path provided: {resume_path}")
    
    results = {}
    for field_key, selector in selector_map.items():
        logger.debug(f"Processing field: {field_key} with selector: {selector}")
        
        # Check if this is a file upload field (for resume)
        if field_key in ["resume_upload", "_systemfield_resume"] and resume_path:
            try:
                logger.debug(f"Attempting to upload resume for field: {field_key}")
                # Use Playwright's file upload method
                # set_input_files() handles file selection dialogs automatically
                page.set_input_files(selector, resume_path)
                results[field_key] = "uploaded"
                logger.info(f"Successfully uploaded resume for field: {field_key}")
            except Exception as e:
                # If file upload fails, record the error but continue
                error_msg = f"upload error: {str(e)}"
                results[field_key] = error_msg
                logger.error(f"Failed to upload resume for field {field_key}: {error_msg}")
                
        # Check if this is a text field we have data for
        elif field_key in data:
            try:
                logger.debug(f"Attempting to fill text field: {field_key} with value: {data[field_key][:20]}...")
                # Use Playwright's text filling method
                # fill() clears the field and types the new text
                page.fill(selector, data[field_key])
                results[field_key] = "filled"
                logger.debug(f"Successfully filled field: {field_key}")
            except Exception as e:
                # If text filling fails, record the error but continue
                error_msg = f"fill error: {str(e)}"
                results[field_key] = error_msg
                logger.error(f"Failed to fill field {field_key}: {error_msg}")
        else:
            # Field exists in the form but we don't have data for it
            results[field_key] = "skipped (no data)"
            logger.warning(f"Skipped field {field_key}: no data available")

    # Log summary of results
    success_count = len([r for r in results.values() if r in ["uploaded", "filled"]])
    error_count = len([r for r in results.values() if "error" in r])
    skip_count = len([r for r in results.values() if "skipped" in r])
    
    logger.info(f"Form filling completed - Success: {success_count}, Errors: {error_count}, Skipped: {skip_count}")
    return results
