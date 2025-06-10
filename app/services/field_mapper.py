# File: app/services/field_mapper.py
"""
FIELD MAPPER SERVICE - AI-powered form field detection and mapping

This is one of the most sophisticated parts of the system. It uses AI to understand
job application forms and create a "map" of how to fill them out automatically.

The Two-Step Process:
1. Browser Automation: Use Playwright to load the job application page and extract HTML
2. AI Analysis: Send the HTML to GPT-4 to identify form fields and create CSS selectors

This solves the problem that every job application form is different - instead of
manually coding for each ATS (Applicant Tracking System), we use AI to understand
any form structure automatically.
"""

from playwright.sync_api import sync_playwright  # Browser automation library
from openai import OpenAI                       # GPT-4 for HTML analysis
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_form_selectors(url: str) -> dict:
    with sync_playwright() as p:
        # Launch a headless Chrome browser (invisible, runs in background)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # === PHASE 1: EXTRACT HTML FROM JOB APPLICATION PAGE ===
            
            # Navigate to the job application URL
            # timeout=60000 means wait up to 60 seconds for page to load
            page.goto(url, timeout=60000)
            
            # Wait 4 seconds for any dynamic content to load
            # Many modern sites use JavaScript to build forms after initial page load
            page.wait_for_timeout(4000)

            # Try to extract just the form HTML (more targeted approach)
            try:
                # Look for a <form> element on the page (most job applications have one)
                page.wait_for_selector("form", timeout=7000)
                # Extract just the HTML inside the form element
                form_html = page.locator("form").inner_html()
            except:
                # If no form found or timeout, we'll use the full page
                form_html = None

            # Use form HTML if found, otherwise use full page content
            # [:24000] limits to first 24,000 characters to avoid API limits
            html = form_html or page.content()[:24000]

            # Save debug snapshot for troubleshooting
            # This helps us see what HTML was extracted if something goes wrong
            with open("uploads/form_snapshot.html", "w", encoding="utf-8") as f:
                f.write(html)

            # Close the browser to free up resources
            browser.close()

            # === PHASE 2: AI ANALYSIS OF HTML ===
            
            # Create a detailed prompt for GPT-4 to analyze the HTML
            prompt = f"""
You are a DOM parsing expert. Analyze the following HTML and return a JSON mapping for all input fields:
Return a JSON object where the keys are those names and the values are the CSS selectors to use.

--- HTML START ---
{html}
--- HTML END ---
"""

            # Send the HTML to GPT-4 for analysis
            response = client.chat.completions.create(
                model="gpt-4o",  # Most capable model for understanding HTML structure
                messages=[
                    {"role": "system", "content": "You are a form-filling assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3  # Low temperature for consistent, reliable output
                # We want GPT-4 to be precise and consistent, not creative
            )

            # Extract the selector mapping from GPT-4's response
            content = response.choices[0].message.content
            
            return {"status": "success", "selector_map": content.strip()}

        except Exception as e:
            # If anything goes wrong during the process, clean up and return error
            browser.close()
            return {"status": "error", "error": str(e)}
