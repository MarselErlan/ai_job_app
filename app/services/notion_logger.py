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
from loguru import logger
from app.services.file_diff import get_project_diff
from app.services.log_formatter import format_daily_log
from app.utils.debug_utils import debug_performance

# Configure Loguru
logger.add(
    "logs/notion_logger.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
)

# Initialize Notion client with API credentials
# The Notion client handles authentication and API communication
logger.debug("Initializing Notion client")
notion = Client(auth=os.getenv("NOTION_API_KEY"))
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

if not os.getenv("NOTION_API_KEY"):
    logger.warning("NOTION_API_KEY not found in environment variables")
if not NOTION_DB_ID:
    logger.warning("NOTION_DB_ID not found in environment variables")

@debug_performance
def log_to_notion(title: str, content: str) -> dict:
    """
    📝 LOG ENTRY TO NOTION DATABASE
    
    Creates a new page in the specified Notion database with the given
    title and content. Handles all API communication and error cases.
    
    Args:
        title (str): Title for the Notion page
        content (str): Markdown content for the page body
        
    Returns:
        dict: Status and page ID or error message
    """
    logger.info(f"Creating new Notion page: {title}")
    logger.debug(f"Content length: {len(content)} characters")
    
    try:
        if not NOTION_DB_ID:
            raise ValueError("NOTION_DB_ID not configured")
            
        logger.debug("Preparing Notion page properties")
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
        
        page_id = response.get("id")
        logger.info(f"✅ Successfully created Notion page: {page_id}")
        logger.debug(f"Page URL: https://notion.so/{page_id.replace('-', '')}")
        
        # Return success with the new page ID
        return {"status": "success", "notion_page_id": page_id}
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to create Notion page: {error_msg}", exc_info=True)
        # Return error details if something goes wrong
        return {"status": "error", "message": error_msg}

@debug_performance
def auto_log_project_update() -> dict:
    """
    🔄 AUTOMATICALLY LOG PROJECT UPDATES
    
    Checks for project changes, formats them into a structured log,
    and creates a new Notion page to document the updates.
    
    Returns:
        dict: Status of the logging operation
    """
    logger.info("Starting automatic project update logging")
    
    try:
        # Get list of changed files
        logger.debug("Checking for project changes")
        changes = get_project_diff()
        
        # If no files changed, don't create a log entry
        if not changes:
            logger.info("No project changes detected")
            return {"status": "no update", "message": "No changes detected in project files today."}

        logger.debug(f"Found {len(changes)} modified files")
        
        # Standard accomplishments for logging
        highlights = [
            "Tailored resume using GPT-4o",
            "Generated PDF with personalized filename", 
            "Mapped application fields with LLM",
            "Auto-filled form with Playwright"
        ]
        logger.debug(f"Adding {len(highlights)} standard highlights")
        
        # Format the changes and accomplishments into a structured log
        logger.debug("Formatting daily log entry")
        log_body = format_daily_log(
            changed_files=changes,  # List of modified files from file diff
            highlights=highlights,
            screenshot="uploads/intelligent_apply.png"  # Standard screenshot location
        )

        # Create a dated title for the Notion page
        title = f"🚀 AI Job App – {datetime.now().strftime('%Y-%m-%d')}"
        logger.debug(f"Created page title: {title}")
        
        # Send the formatted log to Notion
        logger.info("Sending log to Notion")
        result = log_to_notion(title, log_body)
        
        if result["status"] == "success":
            logger.info("✅ Successfully logged project update to Notion")
        else:
            logger.error(f"❌ Failed to log to Notion: {result['message']}")
            
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Auto-logging failed: {error_msg}", exc_info=True)
        return {"status": "error", "message": error_msg}
