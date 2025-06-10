# File: app/services/job_scraper.py
"""
JOB SCRAPER SERVICE - Finds job postings using Google Custom Search

This service searches the internet for job postings using Google's Custom Search API.
It's like having a robot that does Google searches for you and collects job listings.

The process:
1. Takes your job query (e.g., "SDET") and location (e.g., "Chicago")
2. Searches Google using the Custom Search API
3. Returns a list of job postings with titles, URLs, and descriptions

This replaces manually searching job boards - the AI does it automatically.
"""

import os
import requests  # HTTP library for making API calls
from dotenv import load_dotenv
from typing import List

load_dotenv()
API_KEY = os.getenv("API_KEY")
CSE_ID = os.getenv("CSE_ID")


def scrape_google_jobs(query: str, location: str, num_results: int = 10) -> List[dict]:
    search_url = "https://www.googleapis.com/customsearch/v1"
    
    # Combine job query with location for better results
    # This creates searches like "SDET jobs in Chicago" or "Software Engineer jobs in New York"
    full_query = f"{query} jobs in {location}"
    
    # Parameters for the Google API request
    params = {
        "key": API_KEY,         # Your Google API key for authentication
        "cx": CSE_ID,           # Your Custom Search Engine ID
        "q": full_query,        # The search query we constructed above
        "num": num_results      # Number of results to return (max 10 per request)
    }

    # Make HTTP request to Google Custom Search API
    response = requests.get(search_url, params=params)
    # Parse the JSON response from Google
    data = response.json()

    # Extract job information from Google's response
    results = []
    # Loop through each search result Google returned
    for item in data.get("items", []):  # "items" contains the actual search results
        results.append({
            "title": item.get("title"),      # Job title (e.g., "Senior SDET at Google")
            "url": item.get("link"),         # Direct link to job posting
            "snippet": item.get("snippet")   # Brief description of the job
        })

    return results
