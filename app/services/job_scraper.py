# File: app/services/job_scraper.py
"""
ENHANCED JOB SCRAPER SERVICE - Advanced Google Custom Search with LangChain Integration

Enhanced Features from Real-World Success:
1. Refined search queries targeting specific job sites
2. Multiple API calls to get comprehensive results (up to 50 jobs)
3. Smart filtering for actual application links
4. LangChain integration for AI-powered job summarization
5. Better company extraction and data quality

This service now uses proven techniques that successfully find real job application
links from companies like Databricks, Mistral AI, Samsara, xAI, etc.
"""

import os
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
from dotenv import load_dotenv
from app.utils.debug_utils import debug_performance

# LangChain imports for AI-powered summarization
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.utils.debug_utils import (
    debug_api_call, debug_memory, debug_section, 
    debug_log_object
)

# Configure Loguru
logger.add(
    "logs/job_scraper.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
)

load_dotenv()

# Initialize LangChain LLM for job summarization
_llm = None

@debug_performance
def get_langchain_llm():
    """Get or initialize LangChain LLM instance"""
    global _llm
    if _llm is None:
        logger.debug("Initializing LangChain LLM")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            _llm = ChatOpenAI(
                model="gpt-4", 
                temperature=0.2, 
                openai_api_key=openai_api_key
            )
            logger.info("✅ LangChain LLM initialized successfully")
        else:
            logger.warning("⚠️ OPENAI_API_KEY not found - summarization disabled")
    return _llm

# Global API statistics tracking
_api_stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "quota_exceeded_count": 0,
    "total_results_found": 0,
    "last_quota_exceeded": None
}

@debug_performance
def get_api_credentials() -> tuple[str, str]:
    """
    🔑 GET API CREDENTIALS AT RUNTIME
    
    Retrieves API credentials from environment variables at runtime
    to avoid environment loading issues during imports.
    
    Returns:
        tuple[str, str]: (api_key, cse_id) or (None, None) if not found
    """
    logger.debug("Retrieving API credentials")
    api_key = os.getenv("API_KEY") or os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("CSE_ID") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    if not api_key or not cse_id:
        logger.warning("Missing API credentials")
        logger.debug(f"API Key present: {bool(api_key)}, CSE ID present: {bool(cse_id)}")
    else:
        logger.debug("Successfully retrieved API credentials")
    
    return api_key, cse_id

@debug_performance
def get_api_statistics() -> Dict:
    """
    📊 GET COMPREHENSIVE API USAGE STATISTICS
    
    Returns detailed statistics about API usage including
    success rates, quota information, and performance metrics.
    
    Returns:
        Dict: Comprehensive API statistics
    """
    logger.debug("Calculating API statistics")
    stats = _api_stats.copy()
    
    # Calculate derived statistics
    if stats["total_requests"] > 0:
        stats["success_rate"] = (stats["successful_requests"] / stats["total_requests"]) * 100
        stats["failure_rate"] = (stats["failed_requests"] / stats["total_requests"]) * 100
        stats["quota_exceeded_rate"] = (stats["quota_exceeded_count"] / stats["total_requests"]) * 100
    else:
        stats["success_rate"] = 0
        stats["failure_rate"] = 0
        stats["quota_exceeded_rate"] = 0
    
    logger.debug(f"API Stats - Success Rate: {stats['success_rate']:.1f}%, Failures: {stats['failure_rate']:.1f}%")
    return stats

@debug_performance
def is_quota_likely_exceeded() -> bool:
    """
    🚫 CHECK IF API QUOTA IS LIKELY EXCEEDED
    
    Uses heuristics to determine if we should avoid making API requests
    based on recent quota exceeded errors.
    
    Returns:
        bool: True if quota is likely exceeded
    """
    logger.debug("Checking if API quota is likely exceeded")
    
    if _api_stats["quota_exceeded_count"] == 0:
        logger.debug("No quota exceeded events recorded")
        return False
    
    # If quota exceeded rate is very high, likely still exceeded
    if _api_stats["quota_exceeded_rate"] >= 100:
        logger.warning(f"🚫 Quota likely exceeded (rate: {_api_stats['quota_exceeded_rate']:.1f}%)")
        return True
    
    logger.debug(f"Quota status OK (exceeded rate: {_api_stats['quota_exceeded_rate']:.1f}%)")
    return False

@debug_performance
def validate_api_configuration() -> Dict[str, bool]:
    """
    🔧 VALIDATE API CONFIGURATION
    
    Checks if all required API credentials are properly configured.
    
    Returns:
        Dict[str, bool]: Configuration status for each component
    """
    logger.info("Validating API configuration")
    api_key, cse_id = get_api_credentials()
    
    config = {
        "api_key_configured": bool(api_key),
        "cse_id_configured": bool(cse_id),
        "all_configured": bool(api_key and cse_id)
    }
    
    logger.debug("🔧 API Configuration Status:")
    logger.debug(f"   🔑 API Key: {'✅' if config['api_key_configured'] else '❌'} Configured")
    logger.debug(f"   🆔 CSE ID: {'✅' if config['cse_id_configured'] else '❌'} Configured")
    
    if config["all_configured"]:
        logger.info("✅ API configuration complete")
    else:
        logger.warning("⚠️ API configuration incomplete")
    
    return config

@debug_performance
def build_refined_query(job_title: str, location: str = "") -> str:
    """
    🎯 BUILD REFINED SEARCH QUERY FOR REAL JOB RESULTS
    
    Creates optimized search queries that target specific job boards
    and application pages, based on proven successful techniques.
    
    Args:
        job_title (str): The job title to search for
        location (str): Optional location filter
        
    Returns:
        str: Refined search query
    """
    logger.debug(f"Building refined query for job: '{job_title}', location: '{location}'")
    
    # Core job sites that consistently have real application links
    target_sites = [
        "site:linkedin.com/jobs",
        "site:indeed.com", 
        "site:lever.co",
        "site:greenhouse.io",
        "site:smartrecruiters.com",
        "site:ashbyhq.com"
    ]
    
    sites_query = " OR ".join(target_sites)
    logger.debug(f"Using {len(target_sites)} target job sites")
    
    # Build the refined query with quotes for exact job title matching
    if location and location.lower() != "remote":
        refined_query = f'"{job_title}" apply now ({sites_query}) {location}'
        logger.debug("Added location to query")
    else:
        refined_query = f'"{job_title}" apply now ({sites_query})'
        logger.debug("Using location-agnostic query")
    
    logger.info(f"🎯 Generated refined search query: {refined_query}")
    return refined_query

@debug_performance
def filter_application_links(items: List[Dict]) -> List[Dict]:
    """
    🔍 FILTER FOR REAL JOB APPLICATION LINKS
    
    Filters search results to only include links that are likely
    to be actual job application pages.
    
    Args:
        items (List[Dict]): Raw search result items
        
    Returns:
        List[Dict]: Filtered items with application links
    """
    logger.info(f"Filtering {len(items)} job results for application links")
    filtered_items = []
    
    # Keywords that indicate real application links
    application_keywords = ["apply", "jobs", "careers", "position", "job", "hiring"]
    logger.debug(f"Using {len(application_keywords)} application keywords for filtering")
    
    for item in items:
        link = item.get("link", "").lower()
        title = item.get("title", "").lower()
        snippet = item.get("snippet", "").lower()
        
        # Check if link contains application-related keywords
        has_application_keyword = any(keyword in link for keyword in application_keywords)
        
        # Additional quality checks
        is_quality_link = (
            has_application_keyword and
            not any(exclude in link for exclude in ["search", "list", "browse", "category"]) and
            len(link) > 20  # Avoid very short/generic links
        )
        
        if is_quality_link:
            filtered_items.append(item)
            logger.debug(f"✅ Accepted job: {item.get('title', 'Unknown')[:50]}...")
        else:
            logger.debug(f"⏭️ Rejected: {item.get('title', 'Unknown')[:50]}... (quality check failed)")
    
    logger.info(f"🔍 Found {len(filtered_items)} quality application links from {len(items)} results")
    logger.debug(f"Filter rate: {(len(filtered_items)/len(items)*100):.1f}% acceptance")
    return filtered_items

@debug_performance
@debug_api_call
def make_multiple_search_requests(query: str, max_results: int = 50) -> List[Dict]:
    """
    🔄 MAKE MULTIPLE API REQUESTS FOR COMPREHENSIVE RESULTS
    
    Makes multiple Google Custom Search API requests to get up to 50 results,
    working around the 10-result-per-request limitation.
    
    Args:
        query (str): Search query
        max_results (int): Maximum total results to fetch
        
    Returns:
        List[Dict]: Combined search results from all requests
    """
    global _api_stats
    
    logger.info(f"Starting multiple search requests for query: {query}")
    logger.debug(f"Requested max results: {max_results}")
    
    api_key, cse_id = get_api_credentials()
    if not api_key or not cse_id:
        logger.error("❌ API credentials not available")
        return []
    
    all_items = []
    search_url = "https://www.googleapis.com/customsearch/v1"
    
    # Calculate number of requests needed (max 10 results per request)
    num_requests = min((max_results + 9) // 10, 5)  # Limit to 5 requests max
    logger.info(f"🔄 Planning {num_requests} API requests to get {max_results} results")
    
    try:
        for i in range(num_requests):
            start_index = (i * 10) + 1
            logger.debug(f"Making request {i+1}/{num_requests} (start_index: {start_index})")
            
            params = {
                "key": api_key,
                "cx": cse_id,
                "q": query,
                "start": start_index
            }
            
            _api_stats["total_requests"] += 1
            
            try:
                response = requests.get(search_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if "items" in data:
                    items = data["items"]
                    all_items.extend(items)
                    _api_stats["successful_requests"] += 1
                    logger.debug(f"Request {i+1} successful: got {len(items)} items")
                else:
                    logger.warning(f"Request {i+1} returned no items")
                    
            except requests.exceptions.RequestException as e:
                _api_stats["failed_requests"] += 1
                if "quotaExceeded" in str(e):
                    _api_stats["quota_exceeded_count"] += 1
                    _api_stats["last_quota_exceeded"] = datetime.now()
                    logger.error(f"❌ API quota exceeded on request {i+1}")
                else:
                    logger.error(f"❌ Request {i+1} failed: {str(e)}")
                break
                
        _api_stats["total_results_found"] = len(all_items)
        logger.info(f"✅ Search completed: found {len(all_items)} total results")
        logger.debug(f"Success rate: {(_api_stats['successful_requests']/_api_stats['total_requests']*100):.1f}%")
        
        return all_items
        
    except Exception as e:
        logger.error(f"❌ Multiple search requests failed: {str(e)}", exc_info=True)
        return []

@debug_performance
def summarize_job_with_langchain(title: str, snippet: str) -> str:
    """
    🤖 USE LANGCHAIN TO GENERATE AI JOB SUMMARY
    
    Uses LangChain with GPT-4 to create an intelligent summary of the job
    posting that highlights key requirements and responsibilities.
    
    Args:
        title (str): Job title
        snippet (str): Job description snippet
        
    Returns:
        str: AI-generated job summary
    """
    logger.debug(f"Generating AI summary for job: {title}")
    
    llm = get_langchain_llm()
    if not llm:
        logger.warning("LangChain LLM not available - skipping summary")
        return ""
        
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a job description analyst. Create a concise summary highlighting key requirements."),
            ("user", f"Title: {title}\n\nDescription: {snippet}")
        ])
        
        logger.debug("Sending request to LangChain LLM")
        chain = prompt | llm
        summary = chain.invoke({}).content
        
        logger.debug(f"Generated summary length: {len(summary)} characters")
        return summary
        
    except Exception as e:
        logger.error(f"❌ Failed to generate job summary: {str(e)}", exc_info=True)
        return ""

@debug_performance
def parse_enhanced_search_results(items: List[Dict], location: str) -> List[Dict]:
    """
    🔍 PARSE AND ENHANCE SEARCH RESULTS
    
    Processes raw search results to extract structured job information
    and enhance with AI-powered insights.
    
    Args:
        items (List[Dict]): Raw search result items
        location (str): Job location for context
        
    Returns:
        List[Dict]: Enhanced job listings
    """
    logger.info(f"Processing {len(items)} search results with enhanced parsing")
    enhanced_jobs = []
    
    for item in items:
        try:
            title = item.get("title", "").strip()
            url = item.get("link", "").strip()
            snippet = item.get("snippet", "").strip()
            display_link = item.get("displayLink", "").strip()
            
            logger.debug(f"Processing job: {title[:50]}...")
            
            # Extract company name using multiple data points
            company = extract_company_name(title, url, display_link, snippet)
            logger.debug(f"Extracted company: {company}")
            
            # Determine job source/platform
            source = determine_job_source(url, display_link)
            logger.debug(f"Determined source: {source}")
            
            # Calculate job quality score
            quality_score = calculate_job_quality_score(title, url, snippet, company)
            logger.debug(f"Calculated quality score: {quality_score:.2f}")
            
            # Generate AI summary if available
            ai_summary = ""
            if quality_score > 0.7:  # Only summarize high-quality listings
                logger.debug("Generating AI summary for high-quality listing")
                ai_summary = summarize_job_with_langchain(title, snippet)
            
            enhanced_job = {
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "description": snippet,
                "source": source,
                "quality_score": quality_score,
                "ai_summary": ai_summary,
                "enhanced_parsing": True
            }
            
            enhanced_jobs.append(enhanced_job)
            logger.debug(f"Successfully enhanced job listing: {title[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ Failed to enhance job listing: {str(e)}", exc_info=True)
            continue
    
    logger.info(f"✅ Enhanced {len(enhanced_jobs)} job listings")
    return enhanced_jobs

@debug_performance
def extract_company_name(title: str, url: str, display_link: str, snippet: str) -> str:
    """
    🏢 EXTRACT COMPANY NAME FROM JOB DATA
    
    Uses multiple data points to reliably extract the company name,
    with fallback strategies for different formats.
    
    Args:
        title (str): Job title
        url (str): Job URL
        display_link (str): Display URL
        snippet (str): Job description snippet
        
    Returns:
        str: Extracted company name
    """
    logger.debug("Attempting to extract company name")
    
    try:
        # Common patterns in job titles
        patterns = [
            r"at ([A-Z][A-Za-z0-9\s&]+)",  # "at Company Name"
            r"with ([A-Z][A-Za-z0-9\s&]+)",  # "with Company Name"
            r"@ ([A-Z][A-Za-z0-9\s&]+)",  # "@ Company Name"
            r"- ([A-Z][A-Za-z0-9\s&]+)",  # "- Company Name"
        ]
        
        # Try title patterns first
        for pattern in patterns:
            import re
            match = re.search(pattern, title)
            if match:
                company = match.group(1).strip()
                logger.debug(f"Extracted company from title pattern: {company}")
                return company
        
        # Fallback to domain name from URL
        domain = display_link.split('.')[0]
        if domain not in ['www', 'jobs', 'careers']:
            company = domain.capitalize()
            logger.debug(f"Extracted company from domain: {company}")
            return company
        
        logger.warning("Could not extract company name reliably")
        return "Unknown Company"
        
    except Exception as e:
        logger.error(f"❌ Failed to extract company name: {str(e)}", exc_info=True)
        return "Unknown Company"

@debug_performance
def determine_job_source(url: str, display_link: str) -> str:
    """
    🔍 DETERMINE JOB POSTING SOURCE/PLATFORM
    
    Identifies which job platform or ATS the listing is from.
    
    Args:
        url (str): Job listing URL
        display_link (str): Display URL
        
    Returns:
        str: Job source platform name
    """
    logger.debug(f"Determining job source from URL: {url}")
    
    try:
        # Common job platforms and their identifiers
        platforms = {
            "linkedin.com": "LinkedIn",
            "indeed.com": "Indeed",
            "lever.co": "Lever",
            "greenhouse.io": "Greenhouse",
            "smartrecruiters.com": "SmartRecruiters",
            "ashbyhq.com": "Ashby",
            "workday.com": "Workday",
            "jobs.lever.co": "Lever"
        }
        
        # Check URL against known platforms
        for domain, platform in platforms.items():
            if domain in url or domain in display_link:
                logger.debug(f"Identified job source: {platform}")
                return platform
        
        # Fallback to display link domain
        source = display_link.split('.')[0].capitalize()
        logger.debug(f"Using fallback source: {source}")
        return source
        
    except Exception as e:
        logger.error(f"❌ Failed to determine job source: {str(e)}", exc_info=True)
        return "Unknown Source"

@debug_performance
def calculate_job_quality_score(title: str, url: str, snippet: str, company: str) -> float:
    """
    📊 CALCULATE JOB LISTING QUALITY SCORE
    
    Assigns a quality score (0-1) based on multiple factors:
    - Title clarity and professionalism
    - Description completeness
    - Company information
    - URL reliability
    - Platform reputation
    
    Args:
        title (str): Job title
        url (str): Job URL
        snippet (str): Job description
        company (str): Company name
        
    Returns:
        float: Quality score between 0 and 1
    """
    logger.debug(f"Calculating quality score for job: {title}")
    score = 0.0
    
    try:
        # Title quality (0.3)
        title_length = len(title.split())
        title_score = min(0.3, (title_length / 10) * 0.3)
        logger.debug(f"Title score: {title_score:.2f}")
        score += title_score
        
        # Description quality (0.3)
        desc_length = len(snippet.split())
        desc_score = min(0.3, (desc_length / 100) * 0.3)
        logger.debug(f"Description score: {desc_score:.2f}")
        score += desc_score
        
        # Company quality (0.2)
        company_score = 0.0
        if company and company != "Unknown Company":
            company_score = 0.2
        logger.debug(f"Company score: {company_score:.2f}")
        score += company_score
        
        # URL quality (0.2)
        url_score = 0.0
        trusted_domains = ["linkedin.com", "indeed.com", "lever.co", "greenhouse.io"]
        if any(domain in url.lower() for domain in trusted_domains):
            url_score = 0.2
        logger.debug(f"URL score: {url_score:.2f}")
        score += url_score
        
        logger.info(f"Final quality score: {score:.2f}")
        return score
        
    except Exception as e:
        logger.error(f"❌ Failed to calculate quality score: {str(e)}", exc_info=True)
        return 0.0

@debug_performance
def create_enhanced_fallback_jobs(query: str, location: str, num_results: int = 5) -> List[Dict]:
    """
    🔄 CREATE FALLBACK JOB LISTINGS
    
    Generates basic job listings when API requests fail, using
    common job sites and standard structures.
    
    Args:
        query (str): Job search query
        location (str): Job location
        num_results (int): Number of fallback results
        
    Returns:
        List[Dict]: Basic job listings
    """
    logger.info(f"Generating {num_results} fallback job listings")
    
    try:
        # Common tech companies for software roles
        companies = [
            "Google", "Microsoft", "Amazon", "Apple", "Meta",
            "Netflix", "Salesforce", "Adobe", "Twitter", "LinkedIn"
        ]
        
        # Job listing templates
        templates = [
            "{role} at {company}",
            "Senior {role} - {company}",
            "Lead {role} - {company}",
            "{company} - {role} Position",
            "{role} Engineer - {company}"
        ]
        
        fallback_jobs = []
        import random
        
        for i in range(min(num_results, len(companies))):
            company = companies[i]
            template = random.choice(templates)
            title = template.format(role=query, company=company)
            
            job = {
                "title": title,
                "company": company,
                "location": location,
                "url": f"https://www.{company.lower()}.com/careers",
                "description": f"Exciting opportunity for a {query} position at {company}. "
                             f"Join our team in {location} and work on cutting-edge projects.",
                "source": "Direct",
                "quality_score": 0.5,
                "ai_summary": "",
                "is_fallback": True
            }
            
            fallback_jobs.append(job)
            logger.debug(f"Created fallback job: {title}")
        
        logger.info(f"Generated {len(fallback_jobs)} fallback listings")
        return fallback_jobs
        
    except Exception as e:
        logger.error(f"❌ Failed to create fallback jobs: {str(e)}", exc_info=True)
        return []

@debug_performance
@debug_api_call
def scrape_google_jobs_enhanced(query: str, location: str, num_results: int = 50) -> List[dict]:
    """
    🚀 ENHANCED JOB SCRAPING WITH AI FEATURES
    
    Main entry point for job scraping with all enhanced features:
    - Multi-request fetching
    - Smart filtering
    - AI summarization
    - Quality scoring
    - Enhanced parsing
    
    Args:
        query (str): Job search query
        location (str): Job location
        num_results (int): Maximum number of results
        
    Returns:
        List[dict]: Enhanced job listings
    """
    logger.info(f"🚀 Starting enhanced job scraping for: {query} in {location}")
    
    try:
        # Validate API configuration
        config = validate_api_configuration()
        if not config["all_configured"]:
            logger.error("❌ API configuration incomplete")
            return create_enhanced_fallback_jobs(query, location)
            
        # Check API quota
        if is_quota_likely_exceeded():
            logger.warning("⚠️ API quota likely exceeded - using fallback")
            return create_enhanced_fallback_jobs(query, location)
            
        # Build optimized search query
        refined_query = build_refined_query(query, location)
        logger.debug(f"Using refined query: {refined_query}")
        
        # Fetch raw search results
        raw_items = make_multiple_search_requests(refined_query, num_results)
        if not raw_items:
            logger.warning("No search results found - using fallback")
            return create_enhanced_fallback_jobs(query, location)
            
        logger.info(f"Found {len(raw_items)} raw search results")
        
        # Filter for quality application links
        filtered_items = filter_application_links(raw_items)
        logger.debug(f"Filtered to {len(filtered_items)} quality links")
        
        # Enhanced parsing and AI features
        enhanced_jobs = parse_enhanced_search_results(filtered_items, location)
        
        # Sort by quality score
        enhanced_jobs.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        logger.info(f"✅ Job scraping complete - returning {len(enhanced_jobs)} enhanced listings")
        logger.debug(f"Average quality score: {sum(job.get('quality_score', 0) for job in enhanced_jobs) / len(enhanced_jobs):.2f}")
        
        return enhanced_jobs
        
    except Exception as e:
        logger.error(f"❌ Enhanced job scraping failed: {str(e)}", exc_info=True)
        return create_enhanced_fallback_jobs(query, location)

# Maintain backward compatibility - alias the enhanced function
scrape_google_jobs = scrape_google_jobs_enhanced
