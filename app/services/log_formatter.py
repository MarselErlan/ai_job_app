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

def format_daily_log(changed_files: list = None, highlights: list = None, screenshot: str = None) -> str:
    today = datetime.now().strftime("%B %d, %Y")
    log = [f"🗓️ **Day Log – {today}**\n"]

    # Add the accomplishments section if we have highlights
    if highlights:
        log.append("**🚀 Completed**")  # Bold header with rocket emoji
        for item in highlights:
            log.append(f"- {item}")     # Bullet point for each accomplishment
        log.append("")                   # Empty line for spacing

    # Add the files modified section if we have changed files
    if changed_files:
        log.append("**📁 Modules Touched**")  # Bold header with folder emoji
        for path in changed_files:
            # Wrap file paths in code formatting (`backticks`) for better readability
            log.append(f"- `{path}`")
        log.append("")                         # Empty line for spacing

    # Add the screenshot section if we have a screenshot path
    if screenshot:
        log.append("**📸 Screenshot**")        # Bold header with camera emoji
        # Wrap screenshot path in code formatting
        log.append(f"- `{screenshot}`")

    # Join all log lines with newlines to create the final formatted string
    return "\n".join(log)
