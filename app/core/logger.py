# File: app/core/logger.py

import sys
import os
from loguru import logger

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(environment: str = "development"):
    logger.remove()  # Clean existing handlers

    log_level = "DEBUG" if environment == "development" else "WARNING"

    # Console output
    logger.add(sys.stdout,
               level=log_level,
               format="<green>{time:HH:mm:ss}</green> | <cyan>{level}</cyan> | <level>{message}</level>",
               colorize=True)

    # Full log to file
    logger.add(f"{LOG_DIR}/pipeline.log",
               rotation="5 MB",
               retention="10 days",
               level="DEBUG",
               format="{time} | {level} | {message}",
               backtrace=True,
               diagnose=True)

    # Errors only
    logger.add(f"{LOG_DIR}/error.log",
               rotation="1 MB",
               retention="10 days",
               level="ERROR",
               format="{time} | {level} | {message}")

    return logger
