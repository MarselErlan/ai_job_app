# File: app/api/v1/jobs.py
"""
JOB API ENDPOINTS - FastAPI routes for job search and matching

This module provides HTTP endpoints for job-related operations including
job searching, matching, and enhanced searching with LangChain integration.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger

from app.services.job_scraper import scrape_google_jobs
from app.services.enhanced_job_scraper import scrape_google_jobs_enhanced
from app.services.jd_matcher import rank_job_matches
from app.services.resume_parser import embed_resume_text

router = APIRouter()

# === PYDANTIC MODELS FOR REQUEST/RESPONSE VALIDATION ===

class JobSearchRequest(BaseModel):
    """Request model for job searching"""
    query: str
    location: str = "Remote"
    num_results: int = 10

class EnhancedJobSearchRequest(BaseModel):
    """Request model for enhanced job searching with LangChain"""
    query: str
    location: str = "Remote" 
    num_results: int = 25
    use_langchain: bool = True

class JobMatchRequest(BaseModel):
    """Request model for job matching"""
    query: str
    location: str = "Remote"
    resume_text: str
    num_results: int = 10

# === JOB SEARCH ENDPOINTS ===

@router.post("/search")
def search_jobs(payload: JobSearchRequest):
    """
    🔍 BASIC JOB SEARCH
    
    Search for jobs using the standard Google Custom Search API.
    """
    try:
        logger.info(f"🔍 Job search: '{payload.query}' in '{payload.location}'")
        
        jobs = scrape_google_jobs(
            query=payload.query,
            location=payload.location,
            num_results=payload.num_results
        )
        
        return {
            "status": "success",
            "query": payload.query,
            "location": payload.location,
            "jobs_found": len(jobs),
            "jobs": jobs
        }
        
    except Exception as e:
        logger.error(f"❌ Job search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/enhanced")
def search_jobs_enhanced(payload: EnhancedJobSearchRequest):
    """
    🚀 ENHANCED JOB SEARCH WITH LANGCHAIN INTEGRATION
    
    Search for jobs using advanced techniques:
    - Refined queries targeting specific job sites
    - Multiple API calls for comprehensive results  
    - Smart filtering for application links
    - LangChain-powered AI summarization
    - Enhanced company extraction
    - Quality scoring and ranking
    """
    try:
        logger.info(f"🚀 Enhanced job search: '{payload.query}' in '{payload.location}'")
        logger.info(f"🤖 LangChain integration: {'enabled' if payload.use_langchain else 'disabled'}")
        
        jobs = scrape_google_jobs_enhanced(
            query=payload.query,
            location=payload.location,
            num_results=payload.num_results
        )
        
        # Additional metadata about enhanced features
        enhanced_features = {
            "ai_summaries": sum(1 for job in jobs if job.get('ai_summary')),
            "quality_scored": sum(1 for job in jobs if job.get('quality_score')),
            "enhanced_parsing": sum(1 for job in jobs if job.get('enhanced_parsing')),
            "average_quality": sum(job.get('quality_score', 0) for job in jobs) / len(jobs) if jobs else 0
        }
        
        return {
            "status": "success",
            "query": payload.query,
            "location": payload.location,
            "jobs_found": len(jobs),
            "enhanced_features": enhanced_features,
            "jobs": jobs
        }
        
    except Exception as e:
        logger.error(f"❌ Enhanced job search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match")
def match_jobs(payload: JobMatchRequest):
    """
    🧠 INTELLIGENT JOB MATCHING
    
    Search for jobs and rank them by compatibility with the provided resume.
    """
    try:
        logger.info(f"🧠 Job matching: '{payload.query}' for resume compatibility")
        
        # Search for jobs
        jobs = scrape_google_jobs(
            query=payload.query,
            location=payload.location,
            num_results=payload.num_results
        )
        
        if not jobs:
            return {
                "status": "no_jobs",
                "message": "No jobs found for matching"
            }
        
        # Create resume embedding
        resume_embedding = embed_resume_text(payload.resume_text)
        
        if not resume_embedding:
            return {
                "status": "error",
                "message": "Failed to create resume embedding"
            }
        
        # Rank jobs by compatibility
        ranked_jobs = rank_job_matches(jobs, resume_embedding)
        
        return {
            "status": "success",
            "query": payload.query,
            "location": payload.location,
            "total_jobs": len(jobs),
            "ranked_jobs": len(ranked_jobs),
            "top_match_score": ranked_jobs[0].get('score', 0) if ranked_jobs else 0,
            "jobs": ranked_jobs
        }
        
    except Exception as e:
        logger.error(f"❌ Job matching failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-enhanced")
def test_enhanced_features():
    """
    🧪 TEST ENHANCED JOB SEARCH FEATURES
    
    Quick test endpoint to demonstrate enhanced job searching capabilities.
    """
    try:
        logger.info("🧪 Testing enhanced job search features")
        
        # Test with a common job title
        test_jobs = scrape_google_jobs_enhanced(
            query="Software Engineer",
            location="San Francisco",
            num_results=5
        )
        
        # Analyze the enhanced features
        analysis = {
            "total_jobs": len(test_jobs),
            "jobs_with_ai_summary": sum(1 for job in test_jobs if job.get('ai_summary')),
            "jobs_with_quality_score": sum(1 for job in test_jobs if job.get('quality_score')),
            "average_quality_score": sum(job.get('quality_score', 0) for job in test_jobs) / len(test_jobs) if test_jobs else 0,
            "unique_companies": len(set(job.get('company', 'Unknown') for job in test_jobs)),
            "sources": list(set(job.get('source', 'Unknown') for job in test_jobs))
        }
        
        return {
            "status": "success",
            "message": "Enhanced job search test completed",
            "analysis": analysis,
            "sample_jobs": test_jobs[:2]  # Return first 2 jobs as samples
        }
        
    except Exception as e:
        logger.error(f"❌ Enhanced features test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
