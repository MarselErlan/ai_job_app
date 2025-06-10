# File: app/api/v1/jobs.py
"""
JOBS API ENDPOINTS - FastAPI routes for job search and matching

This module provides HTTP endpoints for job discovery and intelligent matching
functionality. It's the "job hunting brain" of your system that finds relevant
opportunities and ranks them by compatibility with your resume.

Available Endpoints:
- POST /search - Search for jobs using Google Custom Search API
- POST /match - Rank jobs by similarity to resume embedding

These endpoints work together in the pipeline:
1. /search finds potential job opportunities
2. /match ranks them by semantic similarity to your resume
3. The best matches are used for tailored applications

The separation allows for flexible usage - you can search once and match
multiple times with different resumes, or use external job sources.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from app.services.job_scraper import scrape_google_jobs
from app.services.jd_matcher import rank_job_matches

router = APIRouter()

# === PYDANTIC MODELS FOR REQUEST/RESPONSE VALIDATION ===

class JobSearchRequest(BaseModel):
    """
    Request model for job search functionality
    
    This validates the search parameters that clients send
    to find relevant job opportunities using Google's API.
    """
    query: str          # Search terms like "SDET", "Software Engineer", "Python Developer"
    location: str       # Geographic location like "Chicago", "Remote", "San Francisco"
    num_results: int = 10  # Number of results to return (default: 10, max depends on API limits)

class JobMatchRequest(BaseModel):
    """
    Request model for job matching functionality
    
    This validates the data needed to rank job opportunities
    by semantic similarity to a resume's AI embedding.
    """
    resume_embedding: List[float]  # 1536-dimensional OpenAI embedding vector
    jobs: List[Dict]               # List of job dictionaries from search results

# === JOB SEARCH ENDPOINTS ===

@router.post("/search")
async def search_jobs(payload: JobSearchRequest):
    jobs = scrape_google_jobs(payload.query, payload.location, payload.num_results)
    
    # Return structured response with job results
    return {"results": jobs}

@router.post("/match")
async def match_jobs(payload: JobMatchRequest):
    ranked = rank_job_matches(payload.jobs, payload.resume_embedding)
    
    # Return structured response with ranked results
    return {"ranked_jobs": ranked}
