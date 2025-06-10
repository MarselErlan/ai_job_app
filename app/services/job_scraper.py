# File: app/services/job_scraper.py
"""
JOB SCRAPER SERVICE - Finds job postings using Google Custom Search

This service searches the internet for job postings using Google's Custom Search API.
It avoids duplicate job applications by checking the database for previously applied URLs.
"""

import os
import requests
from dotenv import load_dotenv
from typing import List
from sqlalchemy.orm import Session
from app.db.models import JobApplication
from app.db.session import SessionLocal

load_dotenv()
API_KEY = os.getenv("API_KEY")
CSE_ID = os.getenv("CSE_ID")


def scrape_google_jobs(query: str, location: str, num_results: int = 10) -> List[dict]:
    search_url = "https://www.googleapis.com/customsearch/v1"
    full_query = f"{query} jobs in {location}"

    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": full_query,
        "num": num_results
    }

    response = requests.get(search_url, params=params)
    data = response.json()

    results = []
    db: Session = SessionLocal()

    for item in data.get("items", []):
        job_url = item.get("link")

        # Check for duplicates in DB
        exists = db.query(JobApplication).filter(JobApplication.job_url == job_url).first()
        if exists:
            continue  # Skip duplicates

        job = {
            "title": item.get("title"),
            "url": job_url,
            "snippet": item.get("snippet")
        }
        results.append(job)

        # Save new job into DB
        db.add(JobApplication(
            job_title=job["title"],
            job_url=job["url"],
            status="pending"
        ))

    db.commit()
    db.close()

    return results
