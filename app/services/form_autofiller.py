# File: app/services/form_autofiller.py

from playwright.sync_api import sync_playwright
import time
import os

def apply_to_ashby_job(url: str, name: str, email: str, phone: str, resume_path: str) -> dict:
    screenshot_path = "uploads/apply_screenshot.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True if you don't want UI
        page = browser.new_page()

        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(3000)

            # Fill form fields using Ashby-specific selectors
            page.wait_for_selector('input[data-testid="Field-name"]', timeout=10000)
            page.fill('input[data-testid="Field-name"]', name)

            page.wait_for_selector('input[data-testid="Field-email"]', timeout=10000)
            page.fill('input[data-testid="Field-email"]', email)

            page.wait_for_selector('input[data-testid="Field-phone"]', timeout=10000)
            page.fill('input[data-testid="Field-phone"]', phone)

            # Upload resume
            page.wait_for_selector('input[type="file"]', timeout=10000)
            page.set_input_files('input[type="file"]', resume_path)
            page.wait_for_timeout(2000)

            # Submit form
            page.click('button[type="submit"]')
            page.wait_for_timeout(3000)

            # Save screenshot after submission
            page.screenshot(path=screenshot_path)

            browser.close()
            return {"status": "success", "screenshot": screenshot_path}

        except Exception as e:
            page.screenshot(path="uploads/error_debug.png")
            browser.close()
            return {"status": "error", "error": str(e)}
