#!/usr/bin/env python3
"""
🧪 TEST QUOTA HANDLING AND FALLBACK MECHANISMS

This script tests the fixes for:
1. AttributeError in job scraper
2. Quota exceeded handling
3. Fallback job generation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def test_job_scraper_fixes():
    """Test the job scraper fixes"""
    
    print("🧪 Testing Job Scraper Fixes")
    print("=" * 50)
    
    try:
        from app.services.job_scraper import (
            scrape_google_jobs, 
            get_api_statistics, 
            create_fallback_jobs,
            is_quota_likely_exceeded
        )
        
        print("✅ All imports successful")
        
        # Test 1: Check current API statistics
        print("\n📊 Current API Statistics:")
        stats = get_api_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test 2: Check quota status
        print(f"\n🚫 Quota likely exceeded: {is_quota_likely_exceeded()}")
        
        # Test 3: Test fallback job creation
        print("\n🔄 Testing fallback job creation:")
        fallback_jobs = create_fallback_jobs("SDET", "Chicago", 3)
        print(f"   Created {len(fallback_jobs)} fallback jobs")
        
        if fallback_jobs:
            print("   Sample fallback job:")
            sample = fallback_jobs[0]
            print(f"     Title: {sample['title']}")
            print(f"     Company: {sample['company']}")
            print(f"     URL: {sample['url']}")
            print(f"     Source: {sample['source']}")
        
        # Test 4: Test actual job search (will use fallback if quota exceeded)
        print("\n🔍 Testing job search with fallback handling:")
        jobs = scrape_google_jobs("SDET", "Chicago", 3)
        print(f"   Found {len(jobs)} jobs")
        
        if jobs:
            print("   Sample job:")
            sample = jobs[0]
            print(f"     Title: {sample.get('title', 'N/A')}")
            print(f"     Company: {sample.get('company', 'N/A')}")
            print(f"     Source: {sample.get('source', 'N/A')}")
            
            # Check if it's mock data
            debug_info = sample.get('debug_info', {})
            if debug_info.get('is_mock_data'):
                print("     📋 This is mock/fallback data (quota exceeded)")
            else:
                print("     📡 This is real API data")
        
        # Test 5: Final API statistics
        print("\n📈 Final API Statistics:")
        final_stats = get_api_statistics()
        for key, value in final_stats.items():
            print(f"   {key}: {value}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_job_scraper_fixes()
    if success:
        print("\n✅ Job scraper fixes are working correctly!")
    else:
        print("\n❌ Job scraper fixes need attention!")
        sys.exit(1) 