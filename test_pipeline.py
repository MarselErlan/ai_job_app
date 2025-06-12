#!/usr/bin/env python3
"""
Test script for the AI Job Application Pipeline
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if all required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "API_KEY", 
        "CSE_ID",
        "NOTION_API_KEY",
        "NOTION_DB_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    else:
        print("✅ All environment variables are set")
        return True

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test core services
        from app.services.resume_parser import extract_text_from_resume, embed_resume_text
        from app.services.enhanced_job_scraper import scrape_google_jobs
        from app.services.jd_matcher import rank_job_matches
        from app.services.resume_tailor import tailor_resume
        from app.services.pdf_generator import save_resume_as_pdf
        from app.services.field_mapper import extract_form_selectors
        from app.services.form_autofiller import apply_to_ashby_job, apply_with_selector_map
        from app.services.notion_logger import log_to_notion
        from app.tasks.pipeline import run_pipeline
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_directories():
    """Test if required directories exist"""
    required_dirs = ["uploads", "logs"]
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"Creating directory: {dir_name}")
            os.makedirs(dir_name, exist_ok=True)
    
    print("✅ All required directories exist")
    return True

def test_pipeline_dry_run():
    """Test the pipeline with a dummy resume if available"""
    # Check if there's a test resume
    test_resume_path = "uploads/test_resume.pdf"
    
    if not os.path.exists(test_resume_path):
        print("ℹ️  No test resume found at 'uploads/test_resume.pdf'")
        print("   Place a resume PDF there to test the full pipeline")
        return True
    
    try:
        print("Testing pipeline with test resume...")
        from app.tasks.pipeline import run_pipeline
        
        # Note: This will make actual API calls, so be careful
        result = run_pipeline(
            file_path=test_resume_path,
            name="Test User",
            email="test@example.com",
            phone="555-123-4567"
        )
        
        if result.get("status") == "success":
            print("✅ Pipeline test completed successfully")
            return True
        else:
            print(f"❌ Pipeline test failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing AI Job Application Pipeline\n")
    
    tests = [
        ("Environment Variables", test_environment),
        ("Module Imports", test_imports),
        ("Directory Structure", test_directories),
        # ("Pipeline Dry Run", test_pipeline_dry_run),  # Uncomment to test with real API calls
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append(result)
    
    print("\n" + "="*50)
    if all(results):
        print("🎉 All tests passed! Your pipeline is ready to use.")
        print("\nNext steps:")
        print("1. Add a resume PDF to 'uploads/' directory")
        print("2. Start the API server: uvicorn app.main:app --reload")
        print("3. Or run the pipeline directly from Python")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 