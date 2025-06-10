# File: app/services/form_executor.py

from playwright.sync_api import Page

def fill_fields(page: Page, selector_map: dict, data: dict, resume_path: str = None):
    results = {}
    for field_key, selector in selector_map.items():
        if field_key in ["resume_upload", "_systemfield_resume"] and resume_path:
            try:
                page.set_input_files(selector, resume_path)
                results[field_key] = "uploaded"
            except Exception as e:
                results[field_key] = f"upload error: {str(e)}"
        elif field_key in data:
            try:
                page.fill(selector, data[field_key])
                results[field_key] = "filled"
            except Exception as e:
                results[field_key] = f"fill error: {str(e)}"
        else:
            results[field_key] = "skipped (no data)"

    return results
