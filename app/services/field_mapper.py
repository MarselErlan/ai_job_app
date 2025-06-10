# File: app/services/field_mapper.py

from playwright.sync_api import sync_playwright
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_form_selectors(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(4000)

            # Try to extract just the form; fallback to full page content
            try:
                page.wait_for_selector("form", timeout=7000)
                form_html = page.locator("form").inner_html()
            except:
                form_html = None

            html = form_html or page.content()[:24000]

            # Save debug snapshot
            with open("uploads/form_snapshot.html", "w", encoding="utf-8") as f:
                f.write(html)

            browser.close()

            # Send HTML to LLM to extract relevant input selectors
            prompt = f"""
You are a DOM parsing expert. Analyze the following HTML and return a JSON mapping for all input fields:
Return a JSON object where the keys are those names and the values are the CSS selectors to use.

--- HTML START ---
{html}
--- HTML END ---
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a form-filling assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            content = response.choices[0].message.content
            return {"status": "success", "selector_map": content.strip()}

        except Exception as e:
            browser.close()
            return {"status": "error", "error": str(e)}
