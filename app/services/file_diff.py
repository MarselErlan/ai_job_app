import os
import hashlib

def hash_file(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_project_diff():
    TRACKED_DIRS = ["app/api", "app/services", "app/tasks"]
    hash_file_path = "logs/.file_hashes"

    new_hashes = {}
    for dir in TRACKED_DIRS:
        for root, _, files in os.walk(dir):
            for file in files:
                full_path = os.path.join(root, file)
                new_hashes[full_path] = hash_file(full_path)

    # Load old hashes
    if os.path.exists(hash_file_path):
        with open(hash_file_path, "r") as f:
            old_hashes = dict(line.strip().split(",") for line in f.readlines())
    else:
        old_hashes = {}

    # Compare
    diffs = []
    for path, new_hash in new_hashes.items():
        if old_hashes.get(path) != new_hash:
            diffs.append(f"🛠️ Updated: {path}")

    # Save new hashes
    with open(hash_file_path, "w") as f:
        for path, h in new_hashes.items():
            f.write(f"{path},{h}\n")

    return diffs
