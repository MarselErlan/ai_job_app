# File: app/services/jd_matcher.py

import os
import openai
import numpy as np
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_text(text: str) -> List[float]:
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def rank_job_matches(jobs: List[Dict], resume_embedding: List[float]) -> List[Dict]:
    scored_jobs = []
    for job in jobs:
        jd_text = job.get("snippet", "") + " " + job.get("title", "")
        job_embedding = embed_text(jd_text)
        similarity = cosine_similarity(resume_embedding, job_embedding)
        job["score"] = similarity
        scored_jobs.append(job)

    ranked = sorted(scored_jobs, key=lambda x: x["score"], reverse=True)
    return ranked
