# File: app/services/file_diff.py
"""
FILE DIFF SERVICE - Tracks changes to codebase files for development monitoring

This service monitors which files in your project have been modified since the last
time it was run. It's like a security camera for your code that helps you track
development progress and include accurate "changed files" in your Notion logs.

How It Works:
1. Creates MD5 hashes of all tracked files
2. Compares with previous hashes stored in logs/.file_hashes
3. Identifies which files have been modified
4. Updates the hash storage for next comparison

This helps with:
- Accurate development logging in Notion
- Tracking which modules were involved in each pipeline run
- Understanding the scope of changes during development
- Maintaining a record of system evolution
"""

import os
import hashlib
from loguru import logger
from app.utils.debug_utils import debug_performance

# Configure Loguru
logger.add(
    "logs/file_diff.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
)

@debug_performance
def hash_file(path):
    """
    Generate MD5 hash for a file's contents.
    
    Args:
        path (str): Path to the file to hash
        
    Returns:
        str: MD5 hash of the file's contents
    """
    try:
        logger.debug(f"Generating hash for file: {path}")
        with open(path, 'rb') as f:
            # Read entire file content and generate MD5 hash
            file_hash = hashlib.md5(f.read()).hexdigest()
            logger.debug(f"Generated hash: {file_hash[:8]}... for {path}")
            return file_hash
    except Exception as e:
        logger.error(f"Error hashing file {path}: {str(e)}")
        raise

@debug_performance
def get_project_diff():
    """
    Compare current file hashes with stored hashes to detect changes.
    
    Returns:
        list: List of strings describing file changes
    """
    logger.info("Starting project diff analysis")
    
    try:
        TRACKED_DIRS = ["app/api", "app/services", "app/tasks"]
        logger.debug(f"Tracking directories: {', '.join(TRACKED_DIRS)}")
        
        # Path where we store file hashes between runs
        hash_file_path = "logs/.file_hashes"
        
        # Generate current hashes for all files in tracked directories
        new_hashes = {}
        total_files = 0
        
        for dir in TRACKED_DIRS:
            logger.debug(f"Scanning directory: {dir}")
            # Walk through each directory recursively
            for root, _, files in os.walk(dir):
                for file in files:
                    # Create full path to the file
                    full_path = os.path.join(root, file)
                    # Generate hash for this file's current contents
                    new_hashes[full_path] = hash_file(full_path)
                    total_files += 1
        
        logger.info(f"Scanned {total_files} files across {len(TRACKED_DIRS)} directories")

        # Load previously stored hashes (if file exists)
        if os.path.exists(hash_file_path):
            logger.debug(f"Loading previous hashes from {hash_file_path}")
            # Read the hash storage file
            with open(hash_file_path, "r") as f:
                # Parse each line: "file_path,hash_value"
                # Create dictionary mapping file paths to their stored hashes
                old_hashes = dict(line.strip().split(",") for line in f.readlines())
            logger.debug(f"Loaded {len(old_hashes)} previous hash entries")
        else:
            # First run - no previous hashes exist
            logger.info("No previous hash file found - first run detected")
            old_hashes = {}

        # Compare current hashes with stored hashes to find changes
        diffs = []
        for path, new_hash in new_hashes.items():
            # Check if this file's hash has changed
            if old_hashes.get(path) != new_hash:
                # File is new or modified - add to changes list
                diffs.append(f"🛠️ Updated: {path}")
                logger.info(f"Detected change in file: {path}")

        # Save current hashes for next comparison
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        logger.debug("Saving current hashes for next comparison")
        
        with open(hash_file_path, "w") as f:
            for path, h in new_hashes.items():
                # Write in CSV format: "file_path,hash_value"
                f.write(f"{path},{h}\n")
        
        logger.info(f"Diff analysis complete. Found {len(diffs)} changed files")
        return diffs

    except Exception as e:
        logger.error(f"Error during project diff analysis: {str(e)}")
        raise
