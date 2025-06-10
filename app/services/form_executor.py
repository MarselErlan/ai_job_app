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

def fill_fields(page: Page, selector_map: dict, data: dict, resume_path: str = None):
    results = {}
    for field_key, selector in selector_map.items():
        # Check if this is a file upload field (for resume)
        if field_key in ["resume_upload", "_systemfield_resume"] and resume_path:
            try:
                # Use Playwright's file upload method
                # set_input_files() handles file selection dialogs automatically
                page.set_input_files(selector, resume_path)
                results[field_key] = "uploaded"
            except Exception as e:
                # If file upload fails, record the error but continue
                results[field_key] = f"upload error: {str(e)}"
                
        # Check if this is a text field we have data for
        elif field_key in data:
            try:
                # Use Playwright's text filling method
                # fill() clears the field and types the new text
                page.fill(selector, data[field_key])
                results[field_key] = "filled"
            except Exception as e:
                # If text filling fails, record the error but continue
                results[field_key] = f"fill error: {str(e)}"
        else:
            # Field exists in the form but we don't have data for it
            results[field_key] = "skipped (no data)"

    return results
