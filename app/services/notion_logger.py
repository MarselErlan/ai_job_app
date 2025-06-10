# File: app/services/notion_logger.py
"""
NOTION LOGGER SERVICE - Integration with Notion for pipeline documentation

This service connects your AI job application system with Notion to automatically
document every pipeline run. It's like having a personal assistant that records
everything you accomplish and organizes it in a beautiful, searchable database.

Notion Integration Benefits:
- Permanent record of all job applications
- Visual documentation with screenshots
- Searchable history of pipeline runs
- Professional logging for portfolio/interviews
- Easy sharing and collaboration
- Automatic organization by date
"""

import os
from notion_client import Client
from datetime import datetime
from app.services.file_diff import get_project_diff
from app.services.log_formatter import format_daily_log

# Initialize Notion client with API credentials
# The Notion client handles authentication and API communication
notion = Client(auth=os.getenv("NOTION_API_KEY"))
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

def log_to_notion(title: str, content: str):
    try:
        # Create a new page in the Notion database
        response = notion.pages.create(
            # Specify which database to add the page to
            parent={"database_id": NOTION_DB_ID},
            
            # Set page properties (appears in database view)
            properties={
                "Name": {  # This is the page title property
                    "title": [
                        {"text": {"content": title}}
                    ]
                }
            },
            
            # Add content to the page body
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
        
        # Return success with the new page ID
        return {"status": "success", "notion_page_id": response.get("id")}
        
    except Exception as e:
        # Return error details if something goes wrong
        return {"status": "error", "message": str(e)}

def auto_log_project_update():
    changes = get_project_diff()
    
    # If no files changed, don't create a log entry
    if not changes:
        return {"status": "no update", "message": "No changes detected in project files today."}

    # Format the changes and accomplishments into a structured log
    log_body = format_daily_log(
        changed_files=changes,  # List of modified files from file diff
        highlights=[
            # Standard accomplishments for any pipeline run
            "Tailored resume using GPT-4o",
            "Generated PDF with personalized filename", 
            "Mapped application fields with LLM",
            "Auto-filled form with Playwright"
        ],
        screenshot="uploads/intelligent_apply.png"  # Standard screenshot location
    )

    # Create a dated title for the Notion page
    title = f"🚀 AI Job App – {datetime.now().strftime('%Y-%m-%d')}"
    
    # Send the formatted log to Notion
    return log_to_notion(title, log_body)
