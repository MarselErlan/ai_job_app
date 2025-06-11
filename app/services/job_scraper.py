# File: app/services/job_scraper.py
"""
JOB SCRAPER SERVICE - Finds job postings using Google Custom Search

This service searches the internet for job postings using Google's Custom Search API.
It provides comprehensive debugging and monitoring capabilities for better development experience.

Key Features:
- Google Custom Search API integration
- Request/response logging
- Performance monitoring
- Error handling with detailed stack traces
- API quota tracking
- Response validation
- Debug statistics collection
"""

import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional
from loguru import logger
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import JobApplication
from app.utils.debug_utils import debug_api_call, debug_memory, debug_log_object, debug_section

load_dotenv()
API_KEY = os.getenv("API_KEY")
CSE_ID = os.getenv("CSE_ID")


# API usage statistics for debugging
_api_stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_results_found": 0,
    "average_response_time": 0.0
}

def get_api_statistics() -> Dict:
    """
    📊 GET GOOGLE CUSTOM SEARCH API USAGE STATISTICS
    
    Returns debugging statistics about API usage including
    request counts, success rates, and performance metrics.
    
    Returns:
        Dict: API usage statistics
    """
    return _api_stats.copy()

def validate_api_configuration() -> Dict[str, bool]:
    """
    🔧 VALIDATE API CONFIGURATION
    
    Checks if required API credentials are properly configured
    and logs any configuration issues for debugging.
    
    Returns:
        Dict[str, bool]: Configuration validation results
    """
    config_status = {
        "api_key_configured": bool(API_KEY and len(API_KEY) > 10),
        "cse_id_configured": bool(CSE_ID and len(CSE_ID) > 10),
        "all_configured": False
    }
    
    config_status["all_configured"] = (
        config_status["api_key_configured"] and 
        config_status["cse_id_configured"]
    )
    
    logger.debug("🔧 API Configuration Status:")
    logger.debug(f"   🔑 API Key: {'✅ Configured' if config_status['api_key_configured'] else '❌ Missing'}")
    logger.debug(f"   🆔 CSE ID: {'✅ Configured' if config_status['cse_id_configured'] else '❌ Missing'}")
    
    if not config_status["all_configured"]:
        logger.warning("⚠️ Google Custom Search API not properly configured!")
        logger.warning("   Please check your API_KEY and CSE_ID environment variables")
    
    return config_status

@debug_api_call
def make_google_search_request(query: str, location: str, num_results: int = 10) -> Optional[Dict]:
    """
    🌐 MAKE GOOGLE CUSTOM SEARCH API REQUEST
    
    Makes the actual API request to Google Custom Search with
    comprehensive error handling and debugging.
    
    Args:
        query (str): Job search query
        location (str): Geographic location
        num_results (int): Number of results to fetch
        
    Returns:
        Optional[Dict]: API response data or None if failed
    """
    global _api_stats
    
    search_url = "https://www.googleapis.com/customsearch/v1"
    full_query = f"{query} jobs in {location}"
    
    logger.debug(f"🔍 Making Google Custom Search request:")
    logger.debug(f"   📝 Query: '{full_query}'")
    logger.debug(f"   📊 Requested results: {num_results}")
    
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": full_query,
        "num": num_results
    }
    
    debug_log_object(params, "API Request Parameters (sanitized)")
    
    try:
        _api_stats["total_requests"] += 1
        
        response = requests.get(search_url, params=params, timeout=30)
        
        logger.debug(f"📡 API Response Status: {response.status_code}")
        logger.debug(f"📏 Response Size: {len(response.content)} bytes")
        
        # Check for API errors
        if response.status_code != 200:
            logger.error(f"❌ Google API Error: Status {response.status_code}")
            logger.error(f"   📄 Response: {response.text[:500]}...")
            _api_stats["failed_requests"] += 1
            return None
        
        data = response.json()
        
        # Check for API quota errors
        if "error" in data:
            error_info = data["error"]
            logger.error(f"❌ Google API Error: {error_info.get('message', 'Unknown error')}")
            logger.error(f"   🔢 Error Code: {error_info.get('code', 'Unknown')}")
            _api_stats["failed_requests"] += 1
            return None
        
        _api_stats["successful_requests"] += 1
        
        # Log search statistics
        search_info = data.get("searchInformation", {})
        total_results = search_info.get("totalResults", "0")
        search_time = search_info.get("searchTime", 0)
        
        logger.debug(f"🎯 Search Results:")
        logger.debug(f"   📊 Total available: {total_results}")
        logger.debug(f"   ⏱️ Search time: {search_time}s")
        logger.debug(f"   📋 Returned items: {len(data.get('items', []))}")
        
        _api_stats["total_results_found"] += len(data.get('items', []))
        
        return data
        
    except requests.exceptions.Timeout:
        logger.error("❌ Google API request timed out (30s)")
        _api_stats["failed_requests"] += 1
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Google API request failed: {str(e)}")
        _api_stats["failed_requests"] += 1
        return None
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in Google API request: {str(e)}")
        _api_stats["failed_requests"] += 1
        return None

def parse_search_results(data: Dict, location: str) -> List[Dict]:
    """
    📋 PARSE GOOGLE SEARCH RESULTS
    
    Parses the API response and extracts job information
    with comprehensive validation and debugging.
    
    Args:
        data (Dict): Google API response data
        location (str): Geographic location for context
        
    Returns:
        List[Dict]: List of parsed job postings
    """
    debug_memory("Start parsing search results")
    
    items = data.get("items", [])
    logger.debug(f"📋 Parsing {len(items)} search result items")
    
    parsed_jobs = []
    
    for idx, item in enumerate(items):
        try:
            # Extract job information
            title = item.get("title", "Unknown Title")
            url = item.get("link", "")
            snippet = item.get("snippet", "")
            display_link = item.get("displayLink", "")
            
            # Basic validation
            if not url:
                logger.warning(f"⚠️ Item {idx+1}: No URL found, skipping")
                continue
                
            # Try to extract company name from various sources
            company_name = None
            
            # Method 1: Try to extract from display link
            if display_link:
                # Common job board patterns
                if "lever.co" in display_link:
                    company_name = display_link.split(".")[0]
                elif "ashbyhq.com" in display_link:
                    company_name = display_link.split(".")[0]
                elif "greenhouse.io" in display_link:
                    # Look for company name in URL structure
                    url_parts = url.split("/")
                    for part in url_parts:
                        if part and part != "boards" and part != "jobs":
                            company_name = part.replace("-", " ").title()
                            break
            
            # Method 2: Try to extract from title
            if not company_name and " at " in title:
                company_parts = title.split(" at ")
                if len(company_parts) > 1:
                    company_name = company_parts[-1].strip()
            
            # Method 3: Try to extract from snippet
            if not company_name and snippet:
                # Look for common patterns like "Company Name is hiring"
                import re
                patterns = [
                    r"(\w+(?:\s+\w+)*)\s+is\s+hiring",
                    r"Join\s+(\w+(?:\s+\w+)*)",
                    r"Apply\s+to\s+(\w+(?:\s+\w+)*)"
                ]
                for pattern in patterns:
                    match = re.search(pattern, snippet, re.IGNORECASE)
                    if match:
                        company_name = match.group(1).strip()
                        break
            
            job = {
                "title": title,
                "url": url,
                "snippet": snippet,
                "company": company_name or "Unknown Company",
                "display_link": display_link,
                "location": location,
                "source": "Google Custom Search"
            }
            
            parsed_jobs.append(job)
            
            logger.debug(f"✅ Parsed job {idx+1}: '{title[:50]}...' at '{company_name}'")
            
        except Exception as e:
            logger.error(f"❌ Error parsing search result item {idx+1}: {str(e)}")
            continue
    
    logger.info(f"📊 Successfully parsed {len(parsed_jobs)} out of {len(items)} search results")
    debug_memory("End parsing search results")
    
    return parsed_jobs

@debug_api_call
def scrape_google_jobs(query: str, location: str, num_results: int = 10) -> List[dict]:
    """
    🔍 MAIN JOB SCRAPING FUNCTION WITH COMPREHENSIVE DEBUGGING
    
    Searches for jobs using Google Custom Search API with extensive
    debugging, error handling, and performance monitoring.
    
    Enhanced Features:
    - API configuration validation
    - Request/response debugging
    - Result parsing with company extraction
    - Performance statistics
    - Error recovery
    - Comprehensive logging
    
    Args:
        query (str): Job search query (e.g., "SDET", "Software Engineer")
        location (str): Geographic location
        num_results (int): Number of results to fetch (max 10 per request)
        
    Returns:
        List[dict]: List of job postings with debugging metadata
    """
    
    debug_memory("Start job scraping")
    logger.info(f"🔍 Starting job search: '{query}' in '{location}' ({num_results} results)")
    
    with debug_section("API Configuration Validation"):
        # Validate API configuration
        config_status = validate_api_configuration()
        if not config_status["all_configured"]:
            logger.error("❌ Cannot proceed with job search: API not configured")
            return []
    
    with debug_section("Google API Request"):
        # Make the API request
        data = make_google_search_request(query, location, num_results)
        if not data:
            logger.error("❌ Failed to get search results from Google API")
            return []
    
    with debug_section("Result Parsing"):
        # Parse the results
        jobs = parse_search_results(data, location)
    
    # Log final statistics
    logger.info(f"🎯 Job scraping completed:")
    logger.info(f"   📊 Found: {len(jobs)} jobs")
    logger.info(f"   🔍 Query: '{query}' in '{location}'")
    
    # Log API usage statistics
    stats = get_api_statistics()
    logger.debug(f"📈 API Usage Statistics:")
    logger.debug(f"   📞 Total requests: {stats['total_requests']}")
    logger.debug(f"   ✅ Successful: {stats['successful_requests']}")
    logger.debug(f"   ❌ Failed: {stats['failed_requests']}")
    logger.debug(f"   📊 Total results found: {stats['total_results_found']}")
    
    # Add debugging metadata to each job
    for job in jobs:
        job["debug_info"] = {
            "scraped_at": logger._core.levels[logger._core._min_level].name,
            "api_request_count": stats['total_requests'],
            "search_query": f"{query} jobs in {location}"
        }
    
    debug_memory("End job scraping")
    return jobs
