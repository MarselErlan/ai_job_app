# File: app/services/log_formatter.py

from datetime import datetime

def format_daily_log(changed_files: list = None, highlights: list = None, screenshot: str = None) -> str:
    today = datetime.now().strftime("%B %d, %Y")
    log = [f"🗓️ **Day Log – {today}**\n"]

    if highlights:
        log.append("**🚀 Completed**")
        for item in highlights:
            log.append(f"- {item}")
        log.append("")

    if changed_files:
        log.append("**📁 Modules Touched**")
        for path in changed_files:
            log.append(f"- `{path}`")
        log.append("")

    if screenshot:
        log.append("**📸 Screenshot**")
        log.append(f"- `{screenshot}`")

    return "\n".join(log)
