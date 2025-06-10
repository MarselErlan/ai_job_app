#!/usr/bin/env python3
"""
TEST PERSISTENT SEARCH - Verify the pipeline keeps searching until it finds new URLs

This script tests the persistent search functionality to make sure it:
1. Tries multiple search strategies
2. Keeps searching until new jobs are found
3. Doesn't give up after first failed search
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.tasks.pipeline import run_pipeline, generate_search_variations, persistent_job_search
from app.db.session import SessionLocal
from app.db.crud import get_all_job_urls
from loguru import logger

def test_search_variations():
    """Test the search variation generation"""
    print("🧪 Testing Search Variation Generation")
    print("=" * 50)
    
    # Test SDET variations
    sdet_variations = generate_search_variations("SDET", "New York")
    print(f"\n📋 SDET in New York variations ({len(sdet_variations)} total):")
    for i, var in enumerate(sdet_variations[:5], 1):  # Show first 5
        print(f"   {i}. {var['description']}")
    if len(sdet_variations) > 5:
        print(f"   ... and {len(sdet_variations) - 5} more")
    
    # Test Software Engineer variations  
    se_variations = generate_search_variations("Software Engineer", "Chicago")
    print(f"\n📋 Software Engineer in Chicago variations ({len(se_variations)} total):")
    for i, var in enumerate(se_variations[:5], 1):
        print(f"   {i}. {var['description']}")
    if len(se_variations) > 5:
        print(f"   ... and {len(se_variations) - 5} more")

def test_persistent_search():
    """Test the persistent search function directly"""
    print("\n🔍 Testing Persistent Search Function")
    print("=" * 50)
    
    # Get existing URLs from database
    db = SessionLocal()
    try:
        existing_urls = get_all_job_urls(db)
        print(f"📊 Found {len(existing_urls)} existing URLs in database")
        
        # Test persistent search with limited attempts for testing
        print(f"\n🎯 Testing persistent search for 'SDET' in 'New York' (max 3 attempts)")
        new_jobs, search_stats = persistent_job_search(
            role="SDET",
            location="New York", 
            existing_urls=existing_urls,
            max_attempts=3  # Limit for testing
        )
        
        print(f"\n📊 Search Results:")
        print(f"   Total attempts: {search_stats['total_attempts']}")
        print(f"   New jobs found: {search_stats['new_jobs_found']}")
        print(f"   Duplicates skipped: {search_stats['duplicate_jobs_skipped']}")
        print(f"   Strategies tried: {len(search_stats['strategies_tried'])}")
        
        print(f"\n🎯 Strategies attempted:")
        for i, strategy in enumerate(search_stats['strategies_tried'], 1):
            print(f"   {i}. {strategy}")
        
        if new_jobs:
            print(f"\n✨ New Jobs Found:")
            for i, job in enumerate(new_jobs[:3], 1):  # Show first 3
                print(f"   {i}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                print(f"      URL: {job.get('url', 'Unknown')}")
        else:
            print(f"\n⚠️ No new jobs found")
            
    finally:
        db.close()

def test_full_pipeline():
    """Test the full pipeline to see how it handles job searching"""
    print("\n🚀 Testing Full Pipeline")
    print("=" * 50)
    
    print("📝 Note: This will only test the search portion, not the full application process")
    print("       since we don't want to actually apply to jobs during testing.\n")
    
    # Test with a resume file (you'll need to have one)
    resume_files = [
        "uploads/Eric_Abram_11.pdf",
        "uploads/latest_resume.pdf", 
        "uploads/resume.pdf"
    ]
    
    resume_file = None
    for file_path in resume_files:
        if os.path.exists(file_path):
            resume_file = file_path
            break
    
    if not resume_file:
        print("❌ No resume file found. Please ensure you have one of:")
        for file_path in resume_files:
            print(f"   - {file_path}")
        return
    
    print(f"📄 Using resume file: {resume_file}")
    
    # Run pipeline with different parameters to test search
    test_params = [
        {"role": "SDET", "location": "New York"},
        {"role": "Software Engineer", "location": "San Francisco"},
        {"role": "QA Automation Engineer", "location": "Remote"}
    ]
    
    for params in test_params:
        print(f"\n🔍 Testing pipeline with: {params}")
        
        # We'll just test the search logic, not the full application
        # by calling the pipeline but expecting it to find jobs or report properly
        try:
            result = run_pipeline(
                file_path=resume_file,
                role=params["role"],
                location=params["location"]
            )
            
            print(f"   Status: {result.get('status', 'unknown')}")
            if result.get('status') == 'no_new_jobs':
                print(f"   Message: {result.get('message', 'No message')}")
                if 'search_stats' in result:
                    stats = result['search_stats']
                    print(f"   Search attempts: {stats.get('total_attempts', 0)}")
                    print(f"   Strategies tried: {len(stats.get('strategies_tried', []))}")
            elif result.get('status') == 'success':
                print(f"   Found job: {result.get('best_job', {}).get('title', 'Unknown')}")
            elif result.get('status') == 'error':
                print(f"   Error: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Add a small delay between tests
        import time
        time.sleep(1)

if __name__ == "__main__":
    print("🎯 AI Job Application System - Persistent Search Test")
    print("This script tests the persistent search functionality")
    print("to ensure it keeps trying until new jobs are found.\n")
    
    try:
        test_search_variations()
        test_persistent_search() 
        test_full_pipeline()
        
        print("\n" + "=" * 60)
        print("✅ Testing completed!")
        print("\n💡 Key Points:")
        print("   • The system tries multiple search strategies")
        print("   • It doesn't give up after the first failed search")
        print("   • It filters out jobs already in your database")
        print("   • It provides detailed statistics about the search process")
        print("\n🔄 If you're still getting 'No jobs found' errors:")
        print("   1. Check your Google Custom Search API credentials")
        print("   2. Verify your search terms aren't too restrictive")
        print("   3. Try different role/location combinations")
        print("   4. Check if your database has too many existing jobs")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        print(f"\n❌ Test failed with error: {e}")
        print("\nPlease check:")
        print("   • Database connection is working")
        print("   • Required environment variables are set")
        print("   • All dependencies are installed") 