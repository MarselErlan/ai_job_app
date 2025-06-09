# File: app/api/v1/jobs.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from app.services.job_scraper import scrape_google_jobs
from app.services.jd_matcher import rank_job_matches

router = APIRouter()

class JobSearchRequest(BaseModel):
    query: str
    location: str
    num_results: int = 10

class JobMatchRequest(BaseModel):
    resume_embedding: List[float]
    jobs: List[Dict]

@router.post("/search")
async def search_jobs(payload: JobSearchRequest):
    jobs = scrape_google_jobs(payload.query, payload.location, payload.num_results)
    return {"results": jobs}

@router.post("/match")
async def match_jobs(payload: JobMatchRequest):
    ranked = rank_job_matches(payload.jobs, payload.resume_embedding)
    return {"ranked_jobs": ranked}
