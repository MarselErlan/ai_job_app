# File: app/services/resume_parser.py
"""
RESUME PARSER SERVICE - Converts PDF resumes into AI-readable format

This service handles the first critical step of the pipeline:
1. Extract text from PDF files (visual → textual)
2. Convert text into AI embeddings (textual → numerical vectors)

The embeddings are used later to find semantic matches with job descriptions.
Think of embeddings as a "fingerprint" of your resume that AI can compare with jobs.
"""

import fitz  # PyMuPDF - Library for reading PDF files
import openai  # OpenAI API for creating embeddings
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # New client instance  

def extract_text_from_resume(pdf_path: str) -> str:
    text = ""
    with fitz.open(pdf_path) as doc:
        # Loop through each page in the PDF
        for page in doc:
            # Extract text from current page and add to our text string
            text += page.get_text()
    
    # Remove extra whitespace and return clean text
    return text.strip()

def embed_resume_text(text: str):
    response = client.embeddings.create(
        input=[text],                    # Your resume text as input
        model="text-embedding-ada-002"   # OpenAI's embedding model (most cost-effective)
    )
    
    # Extract the embedding vector from the API response
    # response.data[0].embedding contains the 1536-dimensional vector
    return response.data[0].embedding
