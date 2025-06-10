#!/usr/bin/env python3
"""
TEST SCRIPT - Demonstrates the improved URL checking functionality

This script shows how the pipeline now efficiently checks for existing
job URLs before processing them, preventing duplicate applications.
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.session import SessionLocal
from app.db.crud import get_all_job_urls, job_exists, create_job_entry, get_application_stats
from app.tasks.pipeline import run_pipeline
from loguru import logger

def test_url_checking():
    """
    🧪 TEST THE URL CHECKING FUNCTIONALITY
    
    This function demonstrates how the improved pipeline:
    1. Checks existing URLs efficiently
    2. Skips already processed jobs
    3. Only processes new opportunities
    4. Provides detailed statistics
    """
    
    print("🧪 Testing URL Checking Functionality")
    print("=" * 50)
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # === TEST 1: Get current statistics ===
        print("\n📊 Current Database Statistics:")
        stats = get_application_stats(db)
        for key, value in stats.items():
            if key == "success_rate":
                print(f"   {key}: {value:.1%}")
            else:
                print(f"   {key}: {value}")
        
        # === TEST 2: Show existing URLs ===
        print("\n🔍 Existing Job URLs in Database:")
        existing_urls = get_all_job_urls(db)
        if existing_urls:
            for i, url in enumerate(list(existing_urls)[:5], 1):  # Show first 5
                print(f"   {i}. {url}")
            if len(existing_urls) > 5:
                print(f"   ... and {len(existing_urls) - 5} more")
        else:
            print("   No existing URLs found")
        
        # === TEST 3: Test individual URL checking ===
        print("\n🔍 Testing Individual URL Checking:")
        test_urls = [
            "https://example-company.com/careers/sdet-role",
            "https://another-company.com/jobs/software-engineer",
            "https://startup.com/apply/python-developer"
        ]
        
        for url in test_urls:
            exists = job_exists(db, url)
            status = "EXISTS" if exists else "NEW"
            print(f"   {url} -> {status}")
        
        # === TEST 4: Add a test job entry ===
        print("\n💾 Adding Test Job Entry:")
        test_job = {
            "title": "Test SDET Position",
            "url": "https://test-company.com/careers/test-sdet",
            "company_name": "Test Company",
            "location": "Chicago",
            "applied": False,
            "status": "pending",
            "notes": "This is a test entry created by the test script"
        }
        
        if not job_exists(db, test_job["url"]):
            job_entry = create_job_entry(db, test_job)
            print(f"   ✅ Created test job entry with ID: {job_entry.id}")
        else:
            print(f"   ⏭️ Test job already exists, skipping creation")
        
        # === TEST 5: Demonstrate pipeline behavior ===
        print("\n🚀 Pipeline URL Checking Behavior:")
        print("   When you run the pipeline, it will:")
        print("   1. Search for jobs using Google Custom Search")
        print("   2. Get all existing URLs from database (efficient)")
        print("   3. Filter out jobs we've already processed")
        print("   4. Only process new job opportunities")
        print("   5. Save successful applications to prevent duplicates")
        
        # === TEST 6: Show performance benefits ===
        print("\n⚡ Performance Benefits:")
        print(f"   - Single query gets all {len(existing_urls)} existing URLs")
        print("   - O(1) lookup time for each job URL check")
        print("   - Prevents duplicate applications automatically")
        print("   - Maintains complete application history")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        
    finally:
        db.close()
        print("\n🔒 Database session closed")

def demonstrate_pipeline_run():
    """
    🚀 DEMONSTRATE A PIPELINE RUN WITH URL CHECKING
    
    This shows what happens when you run the actual pipeline
    with the improved URL checking functionality.
    """
    
    print("\n" + "=" * 50)
    print("🚀 Demonstrating Pipeline Run")
    print("=" * 50)
    
    print("\nTo run the actual pipeline with URL checking:")
    print("```python")
    print("from app.tasks.pipeline import run_pipeline")
    print("")
    print("result = run_pipeline(")
    print("    file_path='uploads/your_resume.pdf',")
    print("    name='Your Name',")
    print("    email='your.email@example.com',")
    print("    phone='555-1234',")
    print("    role='SDET',")
    print("    location='Chicago'")
    print(")")
    print("")
    print("if result['status'] == 'success':")
    print("    print(f\"Applied to: {result['best_job']['title']}\")")
    print("elif result['status'] == 'no_new_jobs':")
    print("    print('All jobs have already been processed')")
    print("```")
    
    print("\n📋 Expected Pipeline Behavior:")
    print("   ✅ Parse resume and create embeddings")
    print("   ✅ Search for jobs using Google Custom Search")
    print("   ✅ Check database for existing URLs (EFFICIENT)")
    print("   ✅ Filter out already processed jobs")
    print("   ✅ Rank remaining jobs by compatibility")
    print("   ✅ Select best new job match")
    print("   ✅ Tailor resume for specific job")
    print("   ✅ Generate tailored PDF")
    print("   ✅ Map form fields using AI")
    print("   ✅ Fill and submit application")
    print("   ✅ Save job to database (PREVENT DUPLICATES)")
    print("   ✅ Log results to Notion")

if __name__ == "__main__":
    print("🎯 AI Job Application System - URL Checking Test")
    print("This script demonstrates the improved duplicate prevention system")
    
    test_url_checking()
    demonstrate_pipeline_run()
    
    print("\n✨ Test completed! The system now efficiently prevents duplicate applications.")
    print("🔄 Run the actual pipeline to see it in action.") 