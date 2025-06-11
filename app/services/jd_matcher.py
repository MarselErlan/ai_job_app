# File: app/services/jd_matcher.py
"""
JOB DESCRIPTION MATCHER SERVICE - AI-powered job relevance ranking

This is the "brain" that matches your resume to job postings using AI.
Instead of simple keyword matching, this uses semantic similarity to understand meaning.

The Magic Process:
1. Convert each job description into AI embeddings (numerical vectors)
2. Compare your resume embedding with each job embedding  
3. Calculate similarity scores using cosine similarity (math that measures vector angles)
4. Rank jobs by relevance score (higher = better match)

Think of it like this:
- Your resume is a point in 1536-dimensional space
- Each job is also a point in that same space
- Jobs closer to your resume point are better matches
- The "distance" is measured using cosine similarity
"""

import os
import openai
import numpy as np  # For mathematical calculations
from typing import List, Dict
from dotenv import load_dotenv
from loguru import logger
from app.utils.debug_utils import debug_performance

# Configure Loguru for this module
logger.add(
    "logs/jd_matcher.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@debug_performance
def embed_text(text: str) -> List[float]:
    """
    Convert text into embeddings using OpenAI's API.
    
    Args:
        text (str): Text to convert to embeddings
        
    Returns:
        List[float]: Embedding vector (1536 dimensions)
    """
    logger.debug(f"Generating embeddings for text (length: {len(text)} chars)")
    try:
        response = client.embeddings.create(
            input=[text],                    # Job description text
            model="text-embedding-ada-002"   # Same model as resume for consistency
        )
        embedding = response.data[0].embedding
        logger.debug(f"Successfully generated embeddings (dimensions: {len(embedding)})")
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        raise

@debug_performance
def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1 (List[float]): First vector
        vec2 (List[float]): Second vector
        
    Returns:
        float: Similarity score between 0.0 and 1.0
    """
    logger.debug(f"Calculating cosine similarity between vectors of dimensions {len(vec1)} and {len(vec2)}")
    try:
        a = np.array(vec1)
        b = np.array(vec2)
        similarity = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        logger.debug(f"Cosine similarity calculated: {similarity:.4f}")
        return similarity
    except Exception as e:
        logger.error(f"Failed to calculate cosine similarity: {str(e)}")
        raise

@debug_performance
def rank_job_matches(jobs: List[Dict], resume_embedding: List[float]) -> List[Dict]:
    """
    Rank jobs based on their similarity to a resume.
    
    Args:
        jobs (List[Dict]): List of job dictionaries containing title and description
        resume_embedding (List[float]): Pre-computed resume embeddings
        
    Returns:
        List[Dict]: Jobs ranked by similarity score
    """
    logger.info(f"Starting job ranking process for {len(jobs)} jobs")
    logger.debug(f"Resume embedding dimensions: {len(resume_embedding)}")
    
    scored_jobs = []
    try:
        for i, job in enumerate(jobs, 1):
            logger.debug(f"Processing job {i}/{len(jobs)}: {job.get('title', 'No title')}")
            
            # Combine job title and description for better matching
            jd_text = job.get("snippet", "") + " " + job.get("title", "")
            logger.debug(f"Combined text length: {len(jd_text)} chars")
            
            try:
                # Convert this job's text into an embedding
                job_embedding = embed_text(jd_text)
                
                # Calculate similarity score
                similarity = cosine_similarity(resume_embedding, job_embedding)
                
                # Add the similarity score to the job data
                job["score"] = similarity
                scored_jobs.append(job)
                
                logger.debug(f"Job {i} scored: {similarity:.4f}")
            except Exception as e:
                logger.error(f"Failed to process job {i}: {str(e)}")
                # Add job with zero score to maintain order
                job["score"] = 0.0
                scored_jobs.append(job)

        # Sort jobs by similarity score
        ranked = sorted(scored_jobs, key=lambda x: x["score"], reverse=True)
        
        # Log ranking summary
        top_score = ranked[0]["score"] if ranked else 0
        avg_score = sum(job["score"] for job in ranked) / len(ranked) if ranked else 0
        logger.info(f"Job ranking completed - Top score: {top_score:.4f}, Average score: {avg_score:.4f}")
        
        return ranked
        
    except Exception as e:
        logger.error(f"Failed to rank jobs: {str(e)}")
        raise
