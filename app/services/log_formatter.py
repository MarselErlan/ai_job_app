# File: app/services/log_formatter.py
"""
LOG FORMATTER SERVICE - Creates structured logs for Notion documentation

This service formats pipeline execution results into clean, readable logs
that get sent to Notion for tracking and review. It's like a professional
reporter that summarizes what happened during each job application attempt.

The formatted logs help you:
- Track what the system accomplished each day
- See which files were modified during development
- Review screenshots of completed applications
- Maintain a history of system usage and improvements
"""

from datetime import datetime
from loguru import logger
from app.utils.debug_utils import debug_performance

# Configure Loguru
logger.add(
    "logs/log_formatter.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
)

@debug_performance
def format_daily_log(changed_files: list = None, highlights: list = None, screenshot: str = None) -> str:
    """
    📝 FORMAT DAILY LOG ENTRY
    
    Creates a nicely formatted Markdown log entry for Notion documentation.
    Includes sections for accomplishments, modified files, and screenshots.
    
    Args:
        changed_files (list, optional): List of modified file paths
        highlights (list, optional): List of completed tasks/highlights
        screenshot (str, optional): Path to screenshot image
        
    Returns:
        str: Formatted log entry in Markdown format
    """
    logger.info("Creating daily log entry")
    logger.debug(f"Input params - Changed files: {len(changed_files) if changed_files else 0}, "
                f"Highlights: {len(highlights) if highlights else 0}, "
                f"Screenshot: {'Yes' if screenshot else 'No'}")
    
    try:
        today = datetime.now().strftime("%B %d, %Y")
        logger.debug(f"Formatting log for date: {today}")
        
        log = [f"🗓️ **Day Log – {today}**\n"]
        logger.debug("Added header section")

        # Add the accomplishments section if we have highlights
        if highlights:
            logger.debug(f"Adding {len(highlights)} highlights")
            log.append("**🚀 Completed**")  # Bold header with rocket emoji
            for item in highlights:
                log.append(f"- {item}")     # Bullet point for each accomplishment
                logger.trace(f"Added highlight: {item}")
            log.append("")                   # Empty line for spacing
        else:
            logger.debug("No highlights to add")

        # Add the files modified section if we have changed files
        if changed_files:
            logger.debug(f"Adding {len(changed_files)} modified files")
            log.append("**📁 Modules Touched**")  # Bold header with folder emoji
            for path in changed_files:
                # Wrap file paths in code formatting (`backticks`) for better readability
                log.append(f"- `{path}`")
                logger.trace(f"Added modified file: {path}")
            log.append("")                         # Empty line for spacing
        else:
            logger.debug("No modified files to add")

        # Add the screenshot section if we have a screenshot path
        if screenshot:
            logger.debug("Adding screenshot section")
            log.append("**📸 Screenshot**")        # Bold header with camera emoji
            # Wrap screenshot path in code formatting
            log.append(f"- `{screenshot}`")
            logger.trace(f"Added screenshot path: {screenshot}")
        else:
            logger.debug("No screenshot to add")

        # Join all log lines with newlines to create the final formatted string
        formatted_log = "\n".join(log)
        logger.info("Successfully created formatted log entry")
        logger.debug(f"Final log length: {len(formatted_log)} characters")
        
        return formatted_log
        
    except Exception as e:
        logger.error(f"Failed to format daily log: {str(e)}", exc_info=True)
        # Return a basic log entry in case of error
        return f"🗓️ **Day Log – {datetime.now().strftime('%B %d, %Y')}**\n\n" \
               f"⚠️ Error formatting log: {str(e)}"
