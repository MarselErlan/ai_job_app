#!/usr/bin/env python3
"""
TEST ENHANCED JOB SEARCH FEATURES

This script demonstrates the advanced job search capabilities
integrated from the user's successful example, including:
- LangChain integration for AI-powered job summarization
- Enhanced company extraction
- Quality scoring and ranking
- Real job application link filtering
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_job_scraper import scrape_google_jobs_enhanced, scrape_google_jobs
from loguru import logger

def test_enhanced_vs_standard():
    """Compare enhanced vs standard job search"""
    
    print("🚀 TESTING ENHANCED JOB SEARCH FEATURES")
    print("=" * 60)
    
    query = "AI Engineer"
    location = "San Francisco"
    
    print(f"\nSearching for: '{query}' in '{location}'")
    print("-" * 40)
    
    # Test standard scraper
    print("\n📊 STANDARD JOB SCRAPER:")
    try:
        standard_jobs = scrape_google_jobs(query, location, 5)
        print(f"   ✅ Found {len(standard_jobs)} jobs")
        for i, job in enumerate(standard_jobs[:2], 1):
            print(f"   {i}. {job.get('title', 'Unknown')[:50]}...")
            print(f"      Company: {job.get('company', 'Unknown')}")
            print(f"      Source: {job.get('source', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Standard scraper failed: {e}")
    
    # Test enhanced scraper
    print("\n🚀 ENHANCED JOB SCRAPER WITH LANGCHAIN:")
    try:
        enhanced_jobs = scrape_google_jobs_enhanced(query, location, 5)
        print(f"   ✅ Found {len(enhanced_jobs)} jobs")
        
        for i, job in enumerate(enhanced_jobs[:2], 1):
            print(f"   {i}. {job.get('title', 'Unknown')[:50]}...")
            print(f"      Company: {job.get('company', 'Unknown')}")
            print(f"      Source: {job.get('source', 'Unknown')}")
            print(f"      Quality Score: {job.get('quality_score', 0):.1f}/10")
            
            ai_summary = job.get('ai_summary', 'No summary')
            if len(ai_summary) > 100:
                ai_summary = ai_summary[:100] + "..."
            print(f"      AI Summary: {ai_summary}")
            print()
        
        # Enhanced features analysis
        analysis = {
            "total_jobs": len(enhanced_jobs),
            "ai_summaries": sum(1 for job in enhanced_jobs if job.get('ai_summary')),
            "quality_scored": sum(1 for job in enhanced_jobs if job.get('quality_score')),
            "enhanced_parsing": sum(1 for job in enhanced_jobs if job.get('enhanced_parsing')),
            "avg_quality": sum(job.get('quality_score', 0) for job in enhanced_jobs) / len(enhanced_jobs) if enhanced_jobs else 0
        }
        
        print("📈 ENHANCED FEATURES ANALYSIS:")
        print(f"   🤖 Jobs with AI summaries: {analysis['ai_summaries']}/{analysis['total_jobs']}")
        print(f"   ⭐ Jobs with quality scores: {analysis['quality_scored']}/{analysis['total_jobs']}")
        print(f"   ✨ Enhanced parsing: {analysis['enhanced_parsing']}/{analysis['total_jobs']}")
        print(f"   📊 Average quality score: {analysis['avg_quality']:.1f}/10")
        
    except Exception as e:
        print(f"   ❌ Enhanced scraper failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Enhanced features test completed!")

def test_langchain_integration():
    """Test LangChain integration specifically"""
    
    print("\n🤖 TESTING LANGCHAIN INTEGRATION")
    print("=" * 40)
    
    from app.services.enhanced_job_scraper import get_langchain_llm, summarize_job_with_langchain
    
    # Test LLM initialization
    llm = get_langchain_llm()
    if llm:
        print("✅ LangChain LLM initialized successfully")
        print(f"   Model: {llm.model_name}")
        print(f"   Temperature: {llm.temperature}")
    else:
        print("❌ LangChain LLM initialization failed")
        return
    
    # Test job summarization
    test_title = "Senior AI Engineer - Machine Learning Platform"
    test_snippet = "Join our team to build cutting-edge AI solutions. We're looking for an experienced engineer with expertise in Python, TensorFlow, and distributed systems. Remote work available with competitive salary and benefits."
    
    print(f"\n📝 Testing job summarization:")
    print(f"   Title: {test_title}")
    print(f"   Snippet: {test_snippet[:100]}...")
    
    summary = summarize_job_with_langchain(test_title, test_snippet)
    print(f"   🤖 AI Summary: {summary}")

if __name__ == "__main__":
    # Run all tests
    test_enhanced_vs_standard()
    test_langchain_integration()
    
    print("\n🎉 All tests completed!")
    print("\n💡 Key Enhanced Features Added:")
    print("   ✅ LangChain integration for AI job summaries")
    print("   ✅ Refined search queries targeting job sites")
    print("   ✅ Enhanced company name extraction")
    print("   ✅ Quality scoring and ranking")
    print("   ✅ Smart filtering for application links")
    print("   ✅ Multiple API calls for comprehensive results") 