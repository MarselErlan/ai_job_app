# File: app/services/notion_logger.py

import os
from notion_client import Client
from datetime import datetime
from app.services.file_diff import get_project_diff
from app.services.log_formatter import format_daily_log

notion = Client(auth=os.getenv("NOTION_API_KEY"))
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

def log_to_notion(title: str, content: str):
    try:
        response = notion.pages.create(
            parent={"database_id": NOTION_DB_ID},
            properties={
                "Name": {
                    "title": [
                        {"text": {"content": title}}
                    ]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": content}}
                        ]
                    }
                }
            ]
        )
        return {"status": "success", "notion_page_id": response.get("id")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def auto_log_project_update():
    changes = get_project_diff()
    if not changes:
        return {"status": "no update", "message": "No changes detected in project files today."}

    log_body = format_daily_log(
        changed_files=changes,
        highlights=[
            "Tailored resume using GPT-4o",
            "Generated PDF with personalized filename",
            "Mapped application fields with LLM",
            "Auto-filled form with Playwright"
        ],
        screenshot="uploads/intelligent_apply.png"
    )

    title = f"🚀 AI Job App – {datetime.now().strftime('%Y-%m-%d')}"
    return log_to_notion(title, log_body)
