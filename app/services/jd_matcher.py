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

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_text(text: str) -> List[float]:
    response = client.embeddings.create(
        input=[text],                    # Job description text
        model="text-embedding-ada-002"   # Same model as resume for consistency
    )
    # Return the embedding vector
    return response.data[0].embedding

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def rank_job_matches(jobs: List[Dict], resume_embedding: List[float]) -> List[Dict]:
    scored_jobs = []
    for job in jobs:
        # Combine job title and description for better matching
        # Both title and snippet contain important information about the role
        jd_text = job.get("snippet", "") + " " + job.get("title", "")
        
        # Convert this job's text into an embedding (same 1536-dimensional space as your resume)
        job_embedding = embed_text(jd_text)
        
        # Calculate how similar this job is to your resume
        # This returns a score from 0.0 (no match) to 1.0 (perfect match)
        similarity = cosine_similarity(resume_embedding, job_embedding)
        
        # Add the similarity score to the job data
        job["score"] = similarity
        
        # Add this scored job to our results list
        scored_jobs.append(job)

    # Sort jobs by similarity score (highest scores first)
    # This puts the most relevant jobs at the beginning of the list
    ranked = sorted(scored_jobs, key=lambda x: x["score"], reverse=True)
    
    return ranked
