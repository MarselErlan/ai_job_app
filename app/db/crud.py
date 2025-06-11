# File: app/db/crud.py
"""
DATABASE CRUD OPERATIONS - Create, Read, Update, Delete operations for job applications

This module handles all database interactions for the job application system.
It provides functions to check for existing jobs, create new entries, and
manage the job application history to prevent duplicates.

Enhanced with comprehensive debugging capabilities:
- Query performance monitoring
- Database transaction logging
- Connection health checking
- Error tracking with stack traces
- Memory usage monitoring for large queries
- SQL query debugging
- Result set validation

Key Functions:
- get_all_job_urls() - Get all existing URLs for efficient duplicate checking
- job_exists() - Check if a specific job URL already exists
- create_job_entry() - Add a new job application to the database
- create_or_ignore_job() - Safe creation that handles duplicates gracefully

Database Schema:
The JobApplication table stores:
- Job details (title, URL, company, location)
- Application status and timestamps
- Resume file paths and screenshots
- Notes and matching scores
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import text
from app.db.models import JobApplication
from loguru import logger
from app.utils.debug_utils import debug_database, debug_memory, debug_section, debug_log_object
import time
from typing import Dict, List, Optional, Tuple

# Database operation statistics for debugging
_db_stats = {
    "total_queries": 0,
    "successful_queries": 0,
    "failed_queries": 0,
    "total_query_time": 0.0,
    "average_query_time": 0.0,
    "longest_query_time": 0.0,
    "total_records_retrieved": 0,
    "total_records_created": 0,
    "connection_errors": 0
}

def get_database_statistics() -> Dict:
    """
    📊 GET DATABASE OPERATION STATISTICS
    
    Returns comprehensive statistics about database operations
    for performance monitoring and debugging.
    
    Returns:
        Dict: Database operation statistics
    """
    stats = _db_stats.copy()
    if stats["total_queries"] > 0:
        stats["average_query_time"] = stats["total_query_time"] / stats["total_queries"]
    return stats

def validate_database_connection(db: Session) -> bool:
    """
    🔌 VALIDATE DATABASE CONNECTION HEALTH
    
    Performs a simple query to check if the database connection
    is working properly and logs any connection issues.
    
    Args:
        db (Session): Database session to test
        
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        # Simple query to test connection
        db.execute(text("SELECT 1"))
        logger.debug("✅ Database connection healthy")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        _db_stats["connection_errors"] += 1
        return False

def log_query_performance(operation_name: str, start_time: float, record_count: int = 0):
    """
    📈 LOG DATABASE QUERY PERFORMANCE STATISTICS
    
    Records and logs performance metrics for database operations
    to help identify slow queries and optimization opportunities.
    
    Args:
        operation_name (str): Name of the database operation
        start_time (float): Start time of the operation
        record_count (int): Number of records affected/retrieved
    """
    global _db_stats
    
    execution_time = time.time() - start_time
    _db_stats["total_queries"] += 1
    _db_stats["total_query_time"] += execution_time
    _db_stats["total_records_retrieved"] += record_count
    
    if execution_time > _db_stats["longest_query_time"]:
        _db_stats["longest_query_time"] = execution_time
    
    logger.debug(f"📊 DB Query: {operation_name}")
    logger.debug(f"   ⏱️ Time: {execution_time:.3f}s")
    logger.debug(f"   📋 Records: {record_count}")
    
    # Warn about slow queries
    if execution_time > 1.0:  # Queries taking longer than 1 second
        logger.warning(f"🐌 Slow query detected: {operation_name} took {execution_time:.3f}s")

@debug_database
def get_all_job_urls(db: Session) -> set[str]:
    """
    🔍 GET ALL EXISTING JOB URLS FOR EFFICIENT DUPLICATE CHECKING
    
    This function retrieves all job URLs currently stored in the database
    and returns them as a set for fast O(1) lookup performance. This is
    much more efficient than checking each URL individually.
    
    Performance Benefits:
    - Single database query instead of N queries
    - Set lookup is O(1) vs O(N) for list checking
    - Reduces database load significantly
    - Enables batch processing of job lists
    
    Args:
        db (Session): Active SQLAlchemy database session
        
    Returns:
        set[str]: Set of all job URLs in the database
        Example: {"https://company1.com/job1", "https://company2.com/job2", ...}
        
    Example Usage:
        existing_urls = get_all_job_urls(db)
        for job in scraped_jobs:
            if job["url"] not in existing_urls:
                # This is a new job we haven't seen before
                process_new_job(job)
    """
    start_time = time.time()
    debug_memory("Before fetching all job URLs")
    
    if not validate_database_connection(db):
        logger.error("❌ Cannot fetch URLs: Database connection failed")
        return set()
    
    try:
        with debug_section("Fetch job URLs query"):
            # Query only the job_url column for efficiency
            # Convert to set for fast membership testing
            result = db.query(JobApplication.job_url).all()
            urls = {row.job_url for row in result if row.job_url}  # Filter out None values
            
        log_query_performance("get_all_job_urls", start_time, len(urls))
        _db_stats["successful_queries"] += 1
        
        logger.debug(f"📊 Retrieved {len(urls)} existing job URLs from database")
        debug_memory("After fetching all job URLs")
        
        # Log sample URLs for debugging (first 3)
        if urls:
            sample_urls = list(urls)[:3]
            logger.debug(f"📋 Sample URLs: {sample_urls}")
        
        return urls
        
    except SQLAlchemyError as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Database error retrieving job URLs: {e}")
        return set()  # Return empty set on error to allow pipeline to continue
    except Exception as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Unexpected error retrieving job URLs: {e}")
        return set()

@debug_database
def create_job_entry(db: Session, job: dict) -> JobApplication:
    """
    💾 CREATE A NEW JOB APPLICATION ENTRY IN THE DATABASE
    
    This function creates a new JobApplication record with all the relevant
    information from a job application attempt. It stores both the job details
    and the application results for future reference.
    
    Database Fields Populated:
    - job_title: The position title
    - job_url: Unique URL of the job posting (used to prevent duplicates)
    - company_name: Name of the hiring company
    - location: Job location (city, state, or "Remote")
    - resume_used: Path to the tailored resume PDF used
    - screenshot_path: Path to screenshot showing successful application
    - applied: Boolean indicating if application was submitted
    - status: Current status ("applied", "pending", "failed")
    - notes: Additional information like match scores
    - applied_at: Timestamp (automatically set by database)
    
    Args:
        db (Session): Active SQLAlchemy database session
        job (dict): Dictionary containing job and application information
            Required keys: "title", "url"
            Optional keys: "company_name", "location", "resume_used", 
                          "screenshot_path", "applied", "status", "notes"
                          
    Returns:
        JobApplication: The created database record with auto-generated ID
        
    Raises:
        IntegrityError: If job URL already exists (violates unique constraint)
        
    Example Usage:
        job_data = {
            "title": "Senior SDET",
            "url": "https://company.com/careers/sdet",
            "company_name": "TechCorp",
            "location": "Chicago",
            "resume_used": "uploads/john_doe_sdet_techcorp.pdf",
            "screenshot_path": "uploads/application_screenshot.png",
            "applied": True,
            "status": "applied",
            "notes": "Auto-applied via pipeline. Match score: 0.89"
        }
        job_entry = create_job_entry(db, job_data)
        print(f"Created job entry with ID: {job_entry.id}")
    """
    start_time = time.time()
    debug_memory("Before creating job entry")
    
    logger.debug(f"💾 Creating job entry for: {job.get('title', 'Unknown')} at {job.get('company_name', 'Unknown Company')}")
    debug_log_object(job, "Job data to be saved")
    
    if not validate_database_connection(db):
        logger.error("❌ Cannot create job: Database connection failed")
        raise SQLAlchemyError("Database connection failed")
    
    try:
        with debug_section("Create job entry transaction"):
            # Validate required fields
            if not job.get("title") or not job.get("url"):
                raise ValueError("Missing required fields: title and url")
            
            # Create new JobApplication instance with provided data
            db_job = JobApplication(
                job_title=job.get("title"),
                job_url=job.get("url"),
                company_name=job.get("company_name"),
                location=job.get("location"),
                resume_used=job.get("resume_used"),
                notes=job.get("notes"),
                screenshot_path=job.get("screenshot_path"),
                applied=job.get("applied", False),
                status=job.get("status", "pending")
            )
            
            logger.debug(f"📝 Adding job to database session")
            
            # Add to session and commit to database
            db.add(db_job)
            db.commit()
            db.refresh(db_job)  # Refresh to get auto-generated fields like ID and timestamp
            
        log_query_performance("create_job_entry", start_time, 1)
        _db_stats["successful_queries"] += 1
        _db_stats["total_records_created"] += 1
        
        logger.info(f"✅ Created job entry: {job.get('title')} at {job.get('company_name')} (ID: {db_job.id})")
        debug_log_object(db_job, "Created job entry")
        debug_memory("After creating job entry")
        
        return db_job
        
    except IntegrityError as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Failed to create job entry - URL already exists: {job.get('url')}")
        logger.debug(f"   💥 Integrity error details: {str(e)}")
        db.rollback()  # Rollback the failed transaction
        raise  # Re-raise the exception for caller to handle
        
    except ValueError as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Invalid job data: {str(e)}")
        debug_log_object(job, "Invalid job data")
        raise
        
    except SQLAlchemyError as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Database error creating job entry: {str(e)}")
        db.rollback()
        raise
        
    except Exception as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Unexpected error creating job entry: {str(e)}")
        db.rollback()
        raise

@debug_database
def job_exists(db: Session, url: str) -> bool:
    """
    🔍 CHECK IF A JOB URL ALREADY EXISTS IN THE DATABASE
    
    This function performs a simple existence check for a specific job URL.
    It's useful for single URL checks, but for multiple URLs, consider using
    get_all_job_urls() for better performance.
    
    The check is based on the job_url field which has a unique constraint
    in the database, ensuring no duplicate applications to the same posting.
    
    Args:
        db (Session): Active SQLAlchemy database session
        url (str): The job URL to check
            Example: "https://company.com/careers/software-engineer"
            
    Returns:
        bool: True if the URL exists in database, False otherwise
        
    Example Usage:
        if job_exists(db, "https://company.com/careers/sdet"):
            print("We've already applied to this job")
        else:
            print("This is a new job opportunity")
            
    Performance Note:
        For checking many URLs, use get_all_job_urls() instead:
        
        # Inefficient for many URLs:
        for job in jobs:
            if job_exists(db, job["url"]):
                continue
                
        # Efficient for many URLs:
        existing_urls = get_all_job_urls(db)
        for job in jobs:
            if job["url"] in existing_urls:
                continue
    """
    start_time = time.time()
    
    if not url:
        logger.warning("⚠️ Empty URL provided to job_exists check")
        return False
    
    logger.debug(f"🔍 Checking existence of URL: {url[:100]}...")
    
    if not validate_database_connection(db):
        logger.error("❌ Cannot check job existence: Database connection failed")
        return False  # Assume it doesn't exist to allow processing
    
    try:
        with debug_section("Job existence check"):
            # Query for the first job with matching URL
            result = db.query(JobApplication).filter_by(job_url=url).first()
            exists = result is not None
            
        log_query_performance("job_exists", start_time, 1 if exists else 0)
        _db_stats["successful_queries"] += 1
        
        logger.debug(f"🔍 URL existence check: {url[:50]}... -> {'EXISTS' if exists else 'NEW'}")
        
        if exists:
            logger.debug(f"📋 Existing job details: {result.job_title} at {result.company_name}")
        
        return exists
        
    except SQLAlchemyError as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Database error checking job existence for {url}: {e}")
        return False  # Assume it doesn't exist to allow processing
        
    except Exception as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Unexpected error checking job existence for {url}: {e}")
        return False

@debug_database
def create_or_ignore_job(db: Session, job: dict) -> tuple[bool, JobApplication | None]:
    """
    🛡️ SAFELY CREATE JOB ENTRY OR IGNORE IF ALREADY EXISTS
    
    This function attempts to create a new job entry but gracefully handles
    the case where the job URL already exists in the database. This is useful
    when you want to avoid duplicate entries without stopping the entire process.
    
    The function uses database-level unique constraints to detect duplicates,
    which is more reliable than checking existence first (avoiding race conditions).
    
    Args:
        db (Session): Active SQLAlchemy database session
        job (dict): Dictionary containing job information
            Required keys: "title", "url"
            Optional keys: "company_name", "location", etc.
            
    Returns:
        tuple[bool, JobApplication | None]: 
            - (True, JobApplication) if job was created successfully
            - (False, None) if job already exists or creation failed
            
    Example Usage:
        job_data = {"title": "SDET", "url": "https://company.com/job", ...}
        created, job_entry = create_or_ignore_job(db, job_data)
        
        if created:
            print(f"New job created with ID: {job_entry.id}")
        else:
            print("Job already exists, skipping...")
            
    Performance Benefits:
    - Atomic operation - no race conditions
    - Single database transaction
    - Handles duplicates gracefully
    - Returns detailed result information
    """
    start_time = time.time()
    debug_memory("Before create_or_ignore_job")
    
    logger.debug(f"🛡️ Attempting safe job creation: {job.get('title', 'Unknown')}")
    
    try:
        with debug_section("Safe job creation attempt"):
            # Try to create the job entry
            job_entry = create_job_entry(db, job)
            
        log_query_performance("create_or_ignore_job (created)", start_time, 1)
        logger.info(f"✅ Successfully created new job: {job.get('title')} (ID: {job_entry.id})")
        debug_memory("After successful job creation")
        
        return True, job_entry
        
    except IntegrityError:
        # Job already exists - this is expected and not an error
        logger.debug(f"ℹ️ Job already exists, ignoring: {job.get('url', 'Unknown URL')}")
        log_query_performance("create_or_ignore_job (ignored)", start_time, 0)
        debug_memory("After job ignored (duplicate)")
        
        return False, None
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in create_or_ignore_job: {str(e)}")
        debug_memory("After job creation error")
        
        return False, None

@debug_database
def get_recent_applications(db: Session, limit: int = 10) -> List[JobApplication]:
    """
    📅 GET RECENT JOB APPLICATIONS WITH DEBUGGING
    
    Retrieves the most recent job applications for monitoring
    and debugging purposes.
    
    Args:
        db (Session): Database session
        limit (int): Maximum number of applications to retrieve
        
    Returns:
        List[JobApplication]: Recent job applications
    """
    start_time = time.time()
    debug_memory("Before fetching recent applications")
    
    logger.debug(f"📅 Fetching {limit} most recent applications")
    
    if not validate_database_connection(db):
        logger.error("❌ Cannot fetch applications: Database connection failed")
        return []
    
    try:
        with debug_section("Fetch recent applications"):
            applications = db.query(JobApplication)\
                           .order_by(JobApplication.applied_at.desc())\
                           .limit(limit)\
                           .all()
                           
        log_query_performance("get_recent_applications", start_time, len(applications))
        _db_stats["successful_queries"] += 1
        
        logger.debug(f"📊 Retrieved {len(applications)} recent applications")
        debug_memory("After fetching recent applications")
        
        return applications
        
    except SQLAlchemyError as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Database error fetching recent applications: {e}")
        return []
        
    except Exception as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Unexpected error fetching recent applications: {e}")
        return []

@debug_database
def get_application_stats(db: Session) -> dict:
    """
    📊 GET COMPREHENSIVE APPLICATION STATISTICS WITH DEBUGGING
    
    This function calculates and returns comprehensive statistics about
    job applications in the database, providing insights into the
    application pipeline performance and success rates.
    
    Enhanced with performance monitoring and detailed logging for
    better debugging and system monitoring capabilities.
    
    Statistics Calculated:
    - Total applications submitted
    - Applications by status (applied, pending, failed, etc.)
    - Applications by location
    - Recent activity (last 7 days, 30 days)
    - Success rates and trends
    - Most active companies
    - Application frequency patterns
    
    Args:
        db (Session): Active SQLAlchemy database session
        
    Returns:
        dict: Comprehensive statistics dictionary with debug metadata
        
    Example Return:
        {
            "total_applications": 45,
            "by_status": {"applied": 40, "pending": 3, "failed": 2},
            "by_location": {"Chicago": 20, "Remote": 15, "New York": 10},
            "recent_activity": {"last_7_days": 12, "last_30_days": 35},
            "success_rate": 0.89,
            "top_companies": [("TechCorp", 5), ("StartupXYZ", 3)],
            "debug_info": {...}
        }
    """
    start_time = time.time()
    debug_memory("Before calculating application stats")
    
    logger.info("📊 Calculating comprehensive application statistics")
    
    if not validate_database_connection(db):
        logger.error("❌ Cannot calculate stats: Database connection failed")
        return {"error": "Database connection failed"}
    
    try:
        with debug_section("Calculate application statistics"):
            from sqlalchemy import func, text
            from datetime import datetime, timedelta
            
            stats = {}
            
            # Basic counts
            logger.debug("📊 Calculating basic counts...")
            total_count = db.query(func.count(JobApplication.id)).scalar()
            stats["total_applications"] = total_count or 0
            
            # Status breakdown
            logger.debug("📊 Calculating status breakdown...")
            status_query = db.query(
                JobApplication.status, 
                func.count(JobApplication.id)
            ).group_by(JobApplication.status).all()
            
            stats["by_status"] = {status: count for status, count in status_query}
            
            # Location breakdown
            logger.debug("📊 Calculating location breakdown...")
            location_query = db.query(
                JobApplication.location,
                func.count(JobApplication.id)
            ).filter(JobApplication.location.isnot(None))\
             .group_by(JobApplication.location).all()
            
            stats["by_location"] = {location: count for location, count in location_query}
            
            # Recent activity
            logger.debug("📊 Calculating recent activity...")
            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            last_7_days = db.query(func.count(JobApplication.id))\
                           .filter(JobApplication.applied_at >= week_ago).scalar() or 0
            last_30_days = db.query(func.count(JobApplication.id))\
                            .filter(JobApplication.applied_at >= month_ago).scalar() or 0
            
            stats["recent_activity"] = {
                "last_7_days": last_7_days,
                "last_30_days": last_30_days
            }
            
            # Success rate (applied vs total)
            applied_count = stats["by_status"].get("applied", 0)
            success_rate = (applied_count / total_count) if total_count > 0 else 0
            stats["success_rate"] = round(success_rate, 3)
            
            # Top companies
            logger.debug("📊 Calculating top companies...")
            company_query = db.query(
                JobApplication.company_name,
                func.count(JobApplication.id)
            ).filter(JobApplication.company_name.isnot(None))\
             .group_by(JobApplication.company_name)\
             .order_by(func.count(JobApplication.id).desc())\
             .limit(10).all()
            
            stats["top_companies"] = [(company, count) for company, count in company_query]
            
            # Add debugging metadata
            stats["debug_info"] = {
                "calculation_time": time.time() - start_time,
                "database_healthy": True,
                "query_count": 6,  # Number of queries executed
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        # Log performance
        log_query_performance("get_application_stats", start_time, total_count)
        _db_stats["successful_queries"] += 1
        
        logger.success(f"📊 Statistics calculated successfully:")
        logger.info(f"   📈 Total applications: {stats['total_applications']}")
        logger.info(f"   ✅ Success rate: {stats['success_rate']:.1%}")
        logger.info(f"   📅 Recent activity: {stats['recent_activity']['last_7_days']} (7 days)")
        
        debug_log_object(stats, "Application statistics")
        debug_memory("After calculating application stats")
        
        return stats
        
    except SQLAlchemyError as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Database error calculating statistics: {e}")
        return {"error": f"Database error: {str(e)}"}
        
    except Exception as e:
        _db_stats["failed_queries"] += 1
        logger.error(f"❌ Unexpected error calculating statistics: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

def log_database_health() -> None:
    """
    🏥 LOG DATABASE HEALTH AND PERFORMANCE SUMMARY
    
    Logs comprehensive database health information including
    performance statistics and connection status.
    """
    stats = get_database_statistics()
    
    logger.info("🏥 DATABASE HEALTH SUMMARY:")
    logger.info(f"   📞 Total queries: {stats['total_queries']}")
    logger.info(f"   ✅ Successful: {stats['successful_queries']}")
    logger.info(f"   ❌ Failed: {stats['failed_queries']}")
    logger.info(f"   ⏱️ Average query time: {stats['average_query_time']:.3f}s")
    logger.info(f"   🐌 Longest query: {stats['longest_query_time']:.3f}s")
    logger.info(f"   📊 Records retrieved: {stats['total_records_retrieved']}")
    logger.info(f"   📝 Records created: {stats['total_records_created']}")
    logger.info(f"   🔌 Connection errors: {stats['connection_errors']}")
    
    # Warn about performance issues
    if stats['average_query_time'] > 0.5:
        logger.warning("⚠️ Average query time is high - consider database optimization")
    
    if stats['connection_errors'] > 0:
        logger.warning(f"⚠️ {stats['connection_errors']} connection errors detected")

# Log database health when module is imported (if debugging is enabled)
import os
if os.getenv("DEBUG_MODE", "true").lower() == "true":
    logger.debug("🔧 CRUD operations debug module initialized")
    # Don't call log_database_health() here as it would require a DB connection
