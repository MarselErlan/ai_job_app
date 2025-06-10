# File: app/services/form_autofiller.py

from playwright.sync_api import sync_playwright
import time
import os
import json
import re

def apply_to_ashby_job(url: str, name: str, email: str, phone: str, resume_path: str) -> dict:
    """Apply to a job using Ashby-specific selectors"""
    screenshot_path = "uploads/apply_screenshot.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True if you don't want UI
        page = browser.new_page()

        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(3000)

            # Fill form fields using Ashby-specific selectors
            try:
                page.wait_for_selector('input[data-testid="Field-name"]', timeout=10000)
                page.fill('input[data-testid="Field-name"]', name)
            except:
                # Try alternative name selectors
                try:
                    page.fill('input[name="name"]', name)
                except:
                    page.fill('input[placeholder*="name" i]', name)

            try:
                page.wait_for_selector('input[data-testid="Field-email"]', timeout=10000)
                page.fill('input[data-testid="Field-email"]', email)
            except:
                # Try alternative email selectors
                try:
                    page.fill('input[name="email"]', email)
                except:
                    page.fill('input[type="email"]', email)

            try:
                page.wait_for_selector('input[data-testid="Field-phone"]', timeout=10000)
                page.fill('input[data-testid="Field-phone"]', phone)
            except:
                # Try alternative phone selectors
                try:
                    page.fill('input[name="phone"]', phone)
                except:
                    page.fill('input[placeholder*="phone" i]', phone)

            # Upload resume
            try:
                page.wait_for_selector('input[type="file"]', timeout=10000)
                page.set_input_files('input[type="file"]', resume_path)
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Resume upload failed: {e}")

            # Submit form (optional - you might want to review before submitting)
            try:
                page.click('button[type="submit"]')
                page.wait_for_timeout(3000)
            except Exception as e:
                print(f"Submit failed (this might be expected): {e}")

            # Save screenshot after submission
            page.screenshot(path=screenshot_path)

            browser.close()
            return {"status": "success", "screenshot": screenshot_path}

        except Exception as e:
            page.screenshot(path="uploads/error_debug.png")
            browser.close()
            return {"status": "error", "error": str(e)}


def apply_with_selector_map(url: str, selector_map: dict, name: str, email: str, phone: str, resume_path: str) -> dict:
    """Apply to a job using dynamically mapped selectors"""
    screenshot_path = "uploads/intelligent_apply.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
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

            # Fill form fields using the selector map
            for field_key, selector in selector_map.items():
                if field_key in ["resume_upload", "_systemfield_resume", "resume"] and resume_path:
                    try:
                        page.set_input_files(selector, resume_path)
                        field_results[field_key] = "uploaded"
                    except Exception as e:
                        field_results[field_key] = f"upload error: {str(e)}"
                elif field_key in data:
                    try:
                        page.fill(selector, data[field_key])
                        field_results[field_key] = "filled"
                    except Exception as e:
                        field_results[field_key] = f"fill error: {str(e)}"
                else:
                    field_results[field_key] = "skipped (no data)"

            # Take screenshot before submitting
            page.screenshot(path=screenshot_path)

            browser.close()
            return {
                "status": "success",
                "fields": field_results,
                "screenshot": screenshot_path
            }

        except Exception as e:
            page.screenshot(path="uploads/intelligent_error.png")
            browser.close()
            return {"status": "error", "error": str(e)}
