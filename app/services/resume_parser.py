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
from loguru import logger
from app.utils.debug_utils import debug_performance

# Configure Loguru
logger.add(
    "logs/resume_parser.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
)

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # New client instance  

@debug_performance
def extract_text_from_resume(pdf_path: str) -> str:
    """
    Extract text content from a PDF resume file.
    
    Args:
        pdf_path (str): Path to the PDF resume file
        
    Returns:
        str: Extracted and cleaned text from the PDF
    """
    logger.info(f"Starting text extraction from PDF: {pdf_path}")
    
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            total_pages = len(doc)
            logger.debug(f"PDF has {total_pages} pages")
            
            # Loop through each page in the PDF
            for page_num, page in enumerate(doc, 1):
                logger.debug(f"Processing page {page_num}/{total_pages}")
                # Extract text from current page and add to our text string
                page_text = page.get_text()
                text += page_text
                logger.debug(f"Extracted {len(page_text)} characters from page {page_num}")
        
        # Remove extra whitespace and return clean text
        cleaned_text = text.strip()
        logger.info(f"Successfully extracted {len(cleaned_text)} characters from PDF")
        return cleaned_text
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        raise

@debug_performance
def embed_resume_text(text: str):
    """
    Convert resume text into embeddings using OpenAI's API.
    
    Args:
        text (str): Cleaned text from the resume
        
    Returns:
        list: Embedding vector (1536-dimensional)
    """
    logger.info(f"Starting embedding generation for text of length {len(text)}")
    
    try:
        response = client.embeddings.create(
            input=[text],                    # Your resume text as input
            model="text-embedding-ada-002"   # OpenAI's embedding model (most cost-effective)
        )
        
        # Extract the embedding vector from the API response
        embedding = response.data[0].embedding
        logger.info(f"Successfully generated embedding vector of dimension {len(embedding)}")
        return embedding
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise
