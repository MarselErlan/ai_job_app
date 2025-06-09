# File: app/services/job_scraper.py

import os
import requests
from dotenv import load_dotenv
from typing import List

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
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("link"),
            "snippet": item.get("snippet")
        })

    return results
