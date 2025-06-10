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

def hash_file(path):
    with open(path, 'rb') as f:
        # Read entire file content and generate MD5 hash
        return hashlib.md5(f.read()).hexdigest()

def get_project_diff():
    TRACKED_DIRS = ["app/api", "app/services", "app/tasks"]
    
    # Path where we store file hashes between runs
    hash_file_path = "logs/.file_hashes"

    # Generate current hashes for all files in tracked directories
    new_hashes = {}
    for dir in TRACKED_DIRS:
        # Walk through each directory recursively
        for root, _, files in os.walk(dir):
            for file in files:
                # Create full path to the file
                full_path = os.path.join(root, file)
                # Generate hash for this file's current contents
                new_hashes[full_path] = hash_file(full_path)

    # Load previously stored hashes (if file exists)
    if os.path.exists(hash_file_path):
        # Read the hash storage file
        with open(hash_file_path, "r") as f:
            # Parse each line: "file_path,hash_value"
            # Create dictionary mapping file paths to their stored hashes
            old_hashes = dict(line.strip().split(",") for line in f.readlines())
    else:
        # First run - no previous hashes exist
        old_hashes = {}

    # Compare current hashes with stored hashes to find changes
    diffs = []
    for path, new_hash in new_hashes.items():
        # Check if this file's hash has changed
        if old_hashes.get(path) != new_hash:
            # File is new or modified - add to changes list
            diffs.append(f"🛠️ Updated: {path}")

    # Save current hashes for next comparison
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    with open(hash_file_path, "w") as f:
        for path, h in new_hashes.items():
            # Write in CSV format: "file_path,hash_value"
            f.write(f"{path},{h}\n")

    return diffs
