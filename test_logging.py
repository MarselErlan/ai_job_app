from app.services.resume_parser import extract_text_from_resume
from app.services.enhanced_job_scraper import scrape_google_jobs
from app.services.jd_matcher import match_resume_to_jd
from app.core.console_logger import set_logger_component
from loguru import logger

def test_logging():
    """Test the component-specific logging system"""
    print("Starting logging test...")
    
    try:
        # Test resume parser
        print("\nTesting resume parser...")
        set_logger_component("resume_parser")
        resume_text = extract_text_from_resume("test_resume.pdf")
        
        # Test job scraper
        print("\nTesting job scraper...")
        set_logger_component("job_scraper")
        jobs = scrape_google_jobs("software engineer", "remote")
        
        # Test JD matcher
        print("\nTesting JD matcher...")
        set_logger_component("jd_matcher")
        match_score = match_resume_to_jd(resume_text, "test job description")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\nError during test: {e}")
        raise

if __name__ == "__main__":
    test_logging() 