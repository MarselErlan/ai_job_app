# File: app/core/console_logger.py

import sys
import os
from loguru import logger

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(environment: str = "development", console_level: str = "DEBUG"):
    """
    Setup logger with enhanced console output for debugging
    
    Args:
        environment: Environment name (development/production)
        console_level: Console log level (DEBUG/INFO/WARNING/ERROR)
    """
    logger.remove()  # Clean existing handlers

    # Enhanced console output with detailed context
    # Show module, function, and line for better debugging
    console_format = (
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{module}</cyan>:<yellow>{function}</yellow>:<magenta>{line}</magenta> | "
        "<level>{message}</level>"
    )
    
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

    # Separate handler for SUCCESS messages with special formatting
    success_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<green>✓ SUCCESS</green> | "
        "<green>{message}</green>"
    )
    
    # Full log to file - Keep ALL debug information in files
    logger.add(f"{LOG_DIR}/pipeline.log",
               rotation="5 MB",
               retention="10 days",
               level="DEBUG",
               format="{time} | {level} | {module}:{function}:{line} | {message}",
               backtrace=True,
               diagnose=True)

    # Errors only with full traceback
    logger.add(f"{LOG_DIR}/error.log",
               rotation="1 MB",
               retention="10 days",
               level="ERROR",
               format="{time} | {level} | {module}:{function}:{line} | {message} | {exception}",
               backtrace=True,
               diagnose=True)

    # Add performance tracking log for timing operations
    logger.add(f"{LOG_DIR}/performance.log",
               rotation="2 MB", 
               retention="5 days",
               level="INFO",
               format="{time} | {module}:{function} | {message}",
               filter=lambda record: "PERF:" in record["message"])

    # Configure based on environment
    if environment == "production":
        # In production, reduce console verbosity but keep file logging detailed
        logger.configure(handlers=[
            {"sink": sys.stdout, "level": "INFO", "format": console_format},
        ])
    
    return logger

def get_contextual_logger(module_name: str):
    """
    Get a logger with module context for better tracing
    
    Args:
        module_name: Name of the module using the logger
        
    Returns:
        Configured logger instance
    """
    return logger.bind(module=module_name)

# Utility functions for common logging patterns
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