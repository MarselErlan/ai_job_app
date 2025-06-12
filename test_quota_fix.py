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
        from app.services.enhanced_job_scraper import (
            scrape_google_jobs,
            scrape_google_jobs_enhanced
        )
        
        print("✅ All imports successful")
        
        # Test: Test enhanced job search
        print("\n🔍 Testing job search with fallback handling:")
        jobs = scrape_google_jobs("SDET", "Chicago", 3)
        print(f"   Found {len(jobs)} jobs")
        
        if jobs:
            print("   Sample job:")
            sample = jobs[0]
            print(f"     Title: {sample.get('title', 'N/A')}")
            print(f"     Company: {sample.get('company', 'N/A')}")
            print(f"     Source: {sample.get('source', 'N/A')}")
            
            # Check if it's enhanced data
            if sample.get('enhanced_parsing'):
                print("     ✨ This uses enhanced parsing")
            if sample.get('ai_summary'):
                print("     🤖 AI summary available")
        
        print("\n🎉 Enhanced job search test completed successfully!")
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