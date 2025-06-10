# File: tests/test_db_insert.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.crud import create_job_entry, get_all_job_urls

test_job = {
    "title": "SDET at TestCorp",
    "url": "https://example.com/job/testcorp-sdet"
}

db = SessionLocal()

if test_job["url"] not in get_all_job_urls(db):
    new_job = create_job_entry(db, test_job)
    print("✅ Job inserted:", new_job.job_title)
else:
    print("⚠️ Job already exists:", test_job["url"])

db.close()
