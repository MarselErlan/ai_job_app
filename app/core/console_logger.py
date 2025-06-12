# File: app/core/console_logger.py

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
import gzip
import shutil

LOG_DIR = "logs"
ARCHIVE_DIR = f"{LOG_DIR}/archive"
CONSOLE_ARCHIVE_DIR = f"{ARCHIVE_DIR}/console"

# Create directories
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)
os.makedirs(CONSOLE_ARCHIVE_DIR, exist_ok=True)

def setup_logger(
    environment: str = "development", 
    console_level: str = "DEBUG",
    enable_console_archive: bool = True,
    archive_strategy: str = "daily"  # daily, hourly, session, size
):
    """
    Setup logger with enhanced console output and archiving
    
    Args:
        environment: Environment name (development/production)
        console_level: Console log level (DEBUG/INFO/WARNING/ERROR)
        enable_console_archive: Whether to archive console output
        archive_strategy: How to archive (daily/hourly/session/size)
    """
    logger.remove()  # Clean existing handlers

    # Enhanced console output with detailed context
    console_format = (
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{module}</cyan>:<yellow>{function}</yellow>:<magenta>{line}</magenta> | "
        "<level>{message}</level>"
    )
    
    # File format (without colors for file storage)
    file_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {module}:{function}:{line} | {message}"
    
    # Add console handler with enhanced formatting
    logger.add(
        sys.stdout,
        level=console_level,
        format=console_format,
        colorize=True,
        # Filter to keep console readable - exclude overly verbose third-party logs
        filter=lambda record: not any(
            noisy_module in record["name"] 
            for noisy_module in ["urllib3", "requests", "httpx", "asyncio", "aiohttp"]
        )
    )

    # 📁 CONSOLE ARCHIVE LOGGING - Mirror console output to files
    if enable_console_archive:
        _setup_console_archive(console_level, file_format, archive_strategy)

    # 📊 CATEGORIZED LOGGING - Different files for different purposes
    _setup_categorized_logging()

    # 🔧 ENVIRONMENT SPECIFIC CONFIGURATION
    if environment == "production":
        _setup_production_logging(console_format)
    
    # 🧹 CLEANUP OLD ARCHIVES
    cleanup_old_archives(days_to_keep=30)
    
    return logger

def _setup_console_archive(console_level: str, file_format: str, archive_strategy: str):
    """Setup console output archiving with different strategies"""
    
    if archive_strategy == "daily":
        # Daily rotation - one file per day
        logger.add(
            f"{CONSOLE_ARCHIVE_DIR}/console_{{time:YYYY-MM-DD}}.log",
            level=console_level,
            format=file_format,
            rotation="00:00",  # Rotate at midnight
            retention="30 days",
            compression="gz",
            filter=lambda record: not any(
                noisy_module in record["name"] 
                for noisy_module in ["urllib3", "requests", "httpx", "asyncio", "aiohttp"]
            )
        )
        
    elif archive_strategy == "hourly":
        # Hourly rotation - one file per hour
        logger.add(
            f"{CONSOLE_ARCHIVE_DIR}/console_{{time:YYYY-MM-DD_HH}}.log",
            level=console_level,
            format=file_format,
            rotation="1 hour",
            retention="7 days",
            compression="gz"
        )
        
    elif archive_strategy == "session":
        # Session-based - one file per application run
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.add(
            f"{CONSOLE_ARCHIVE_DIR}/console_session_{session_timestamp}.log",
            level=console_level,
            format=file_format,
            retention=20  # Keep last 20 files (FIXED: removed "files" text)
        )
        
    elif archive_strategy == "size":
        # Size-based rotation
        logger.add(
            f"{CONSOLE_ARCHIVE_DIR}/console.log",
            level=console_level,
            format=file_format,
            rotation="10 MB",
            retention=15,  # Keep 15 files (FIXED: removed "files" text)
            compression="gz"
        )

def _setup_categorized_logging():
    """Setup different log files for different categories"""
    
    # 🚀 APPLICATION FLOW - Track major application events
    logger.add(
        f"{LOG_DIR}/app_flow.log",
        rotation="5 MB",
        retention="10 days", 
        level="INFO",
        format="{time} | {level} | {module}:{function} | {message}",
        filter=lambda record: any(
            keyword in record["message"].upper() 
            for keyword in ["STARTING", "COMPLETED", "PROCESSING", "GENERATED", "SAVED"]
        )
    )
    
    # 🗄️ DATABASE OPERATIONS
    logger.add(
        f"{LOG_DIR}/database.log",
        rotation="2 MB",
        retention="7 days",
        level="DEBUG", 
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        filter=lambda record: any(
            db_keyword in record["message"].upper()
            for db_keyword in ["DB", "DATABASE", "QUERY", "SQL", "INSERT", "UPDATE", "DELETE", "SELECT"]
        )
    )
    
    # 🌐 API CALLS AND EXTERNAL SERVICES
    logger.add(
        f"{LOG_DIR}/api_calls.log", 
        rotation="3 MB",
        retention="7 days",
        level="INFO",
        format="{time} | {level} | {module}:{function} | {message}",
        filter=lambda record: any(
            api_keyword in record["message"].upper()
            for api_keyword in ["API", "HTTP", "REQUEST", "RESPONSE", "OPENAI", "CLAUDE"]
        )
    )
    
    # 📄 FILE OPERATIONS 
    logger.add(
        f"{LOG_DIR}/file_operations.log",
        rotation="2 MB", 
        retention="5 days",
        level="DEBUG",
        format="{time} | {level} | {module}:{function} | {message}",
        filter=lambda record: any(
            file_keyword in record["message"].upper()
            for file_keyword in ["PDF", "FILE", "SAVE", "LOAD", "READ", "WRITE", "RESUME"]
        )
    )

    # ⚠️ WARNINGS AND ISSUES
    logger.add(
        f"{LOG_DIR}/warnings.log",
        rotation="1 MB",
        retention="10 days", 
        level="WARNING",
        format="{time} | {level} | {module}:{function}:{line} | {message} | {exception}",
        backtrace=True,
        diagnose=True
    )

    # 🔥 ERRORS WITH FULL CONTEXT
    logger.add(f"{LOG_DIR}/error.log",
               rotation="1 MB",
               retention="10 days",
               level="ERROR", 
               format="{time} | {level} | {module}:{function}:{line} | {message} | {exception}",
               backtrace=True,
               diagnose=True)

    # ⏱️ PERFORMANCE METRICS
    logger.add(f"{LOG_DIR}/performance.log",
               rotation="2 MB",
               retention="5 days",
               level="INFO",
               format="{time} | {module}:{function} | {message}",
               filter=lambda record: any(
                   perf_keyword in record["message"].upper()
                   for perf_keyword in ["PERF:", "SLOW", "MEMORY", "TIME:", "DURATION"]
               ))

def _setup_production_logging(console_format: str):
    """Configure logging for production environment"""
    # In production, reduce console verbosity but keep detailed file logging
    logger.configure(handlers=[
        {
            "sink": sys.stdout, 
            "level": "INFO", 
            "format": console_format,
            "filter": lambda record: record["level"].name in ["INFO", "WARNING", "ERROR", "CRITICAL"]
        },
    ])

def cleanup_old_archives(days_to_keep: int = 30):
    """Clean up old archive files to prevent disk space issues"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        archive_path = Path(ARCHIVE_DIR)
        
        for file_path in archive_path.rglob("*.log*"):
            if file_path.stat().st_mtime < cutoff_date.timestamp():
                file_path.unlink()
                logger.debug(f"🧹 Cleaned up old archive: {file_path}")
                
    except Exception as e:
        logger.warning(f"Failed to cleanup archives: {e}")

def compress_old_logs(days_old: int = 7):
    """Compress log files older than specified days"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        log_path = Path(LOG_DIR)
        
        for file_path in log_path.glob("*.log"):
            if file_path.stat().st_mtime < cutoff_date.timestamp():
                compressed_path = file_path.with_suffix(f"{file_path.suffix}.gz")
                
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                file_path.unlink()  # Remove original
                logger.info(f"🗜️ Compressed log: {file_path} -> {compressed_path}")
                
    except Exception as e:
        logger.warning(f"Failed to compress logs: {e}")

def get_console_archive_info():
    """Get information about console archives"""
    try:
        archive_path = Path(CONSOLE_ARCHIVE_DIR)
        archives = list(archive_path.glob("*.log*"))
        
        info = {
            "total_archives": len(archives),
            "total_size_mb": sum(f.stat().st_size for f in archives) / (1024 * 1024),
            "oldest_archive": min(archives, key=lambda f: f.stat().st_mtime).name if archives else None,
            "newest_archive": max(archives, key=lambda f: f.stat().st_mtime).name if archives else None,
            "archive_list": [f.name for f in sorted(archives, key=lambda f: f.stat().st_mtime, reverse=True)]
        }
        
        logger.info(f"📁 Archive Info: {info['total_archives']} files, {info['total_size_mb']:.1f}MB total")
        return info
        
    except Exception as e:
        logger.error(f"Failed to get archive info: {e}")
        return {}

# Enhanced utility functions
def get_contextual_logger(module_name: str):
    """Get a logger with module context for better tracing"""
    return logger.bind(module=module_name)

def log_session_start(session_info: dict = None):
    """Log the start of a new session with context"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"🚀 SESSION START: {timestamp}")
    if session_info:
        for key, value in session_info.items():
            logger.info(f"   📋 {key}: {value}")

def log_session_end(session_stats: dict = None):
    """Log the end of a session with statistics"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    logger.info(f"🏁 SESSION END: {timestamp}")
    if session_stats:
        for key, value in session_stats.items():
            logger.info(f"   📊 {key}: {value}")

def log_function_entry(func_name: str, **kwargs):
    """Log function entry with parameters"""
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"ENTER {func_name}({params})")

def log_function_exit(func_name: str, result=None):
    """Log function exit with result"""
    if result is not None:
        logger.debug(f"EXIT {func_name} -> {type(result).__name__}: {str(result)[:100]}")
    else:
        logger.debug(f"EXIT {func_name}")

def log_performance(operation: str, duration: float):
    """Log performance metrics"""
    logger.info(f"PERF: {operation} took {duration:.3f}s")

def log_data_flow(step: str, data_info: str):
    """Log data transformation steps"""
    logger.debug(f"DATA: {step} | {data_info}")

# Setup with different archive strategies
logger = setup_logger("development", "DEBUG", archive_strategy="daily")
logger = setup_logger("development", "INFO", archive_strategy="session") 
logger = setup_logger("production", "WARNING", archive_strategy="size")

# Session tracking
log_session_start({"user": "developer", "environment": "dev", "version": "1.0"})
# ... your application runs ...
log_session_end({"processed_jobs": 15, "errors": 0, "duration": "45.2s"})

# Get archive information
archive_info = get_console_archive_info()