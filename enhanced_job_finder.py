#!/usr/bin/env python3
"""
ENHANCED JOB FINDER - Real Job Application Links with LangChain

This script replicates the successful approach from your example that found
48 real job application links from companies like Databricks, Mistral AI, Samsara, etc.

Enhanced with:
- LangChain integration for AI-powered job summarization  
- Refined search queries targeting specific job sites
- Smart filtering for actual application links
- Quality scoring and ranking
- File export functionality

Based on your proven techniques that successfully found real jobs at:
- Databricks, Mistral AI, Samsara, xAI, Outschool, SentinelOne, etc.
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_job_scraper import (
    scrape_google_jobs_enhanced, 
    build_refined_query
)

def save_enhanced_results_to_file(jobs, job_title, filename=None):
    """Save enhanced job search results to file like your successful example"""
    
    if not filename:
        filename = f"enhanced_{job_title.lower().replace(' ', '_')}_jobs.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Enhanced job application links for: {job_title}\n")
        f.write(f"Total found: {len(jobs)}\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        for i, job in enumerate(jobs, 1):
            f.write(f"JOB #{i}\n")
            f.write(f"URL: {job.get('url', 'No URL')}\n")
            f.write(f"Title: {job.get('title', 'Unknown')}\n")
            f.write(f"Company: {job.get('company', 'Unknown')}\n")
            f.write(f"Source Platform: {job.get('source', 'Unknown')}\n")
            f.write(f"Quality Score: {job.get('quality_score', 0):.1f}/10\n")
            f.write(f"Location: {job.get('location', 'Unknown')}\n")
            f.write(f"Enhanced Parsing: {'Yes' if job.get('enhanced_parsing') else 'No'}\n")
            f.write(f"\nAI Summary: {job.get('ai_summary', 'No summary available')}\n")
            f.write(f"\nOriginal Snippet: {job.get('snippet', 'No snippet')}\n")
            f.write("-" * 80 + "\n\n")
    
    return filename

def main():
    """Main function to run enhanced job search"""
    
    print("🚀 ENHANCED JOB FINDER - Real Application Links with LangChain")
    print("=" * 80)
    print("Based on your proven techniques that found 48 real jobs!")
    print("Companies found: Databricks, Mistral AI, Samsara, xAI, Outschool, etc.")
    print("=" * 80)
    
    # Job search parameters (customize these)
    job_title = "AI Engineer"  # Change this to your desired role
    location = "San Francisco"  # Change this to your desired location
    max_results = 15  # Number of jobs to find
    
    print(f"\n🔍 Searching for: '{job_title}' in '{location}'")
    print(f"📊 Max results: {max_results}")
    
    # Show the refined query that targets job sites
    refined_query = build_refined_query(job_title, location)
    print(f"\n🎯 Refined search query:")
    print(f"   {refined_query}")
    print("\n📋 This targets: LinkedIn, Indeed, Lever, Greenhouse, SmartRecruiters, Ashby")
    
    # Run enhanced job search
    print(f"\n🚀 Running enhanced job search...")
    try:
        jobs = scrape_google_jobs_enhanced(job_title, location, max_results)
        
        if not jobs:
            print("❌ No jobs found")
            return
        
        print(f"\n✅ Found {len(jobs)} enhanced job opportunities!")
        
        # Display results summary
        print(f"\n📈 ENHANCED SEARCH RESULTS:")
        print(f"   🎯 Total jobs found: {len(jobs)}")
        print(f"   🤖 Jobs with AI summaries: {sum(1 for job in jobs if job.get('ai_summary'))}")
        print(f"   ⭐ Jobs with quality scores: {sum(1 for job in jobs if job.get('quality_score'))}")
        print(f"   ✨ Enhanced parsing: {sum(1 for job in jobs if job.get('enhanced_parsing'))}")
        
        if jobs:
            avg_quality = sum(job.get('quality_score', 0) for job in jobs) / len(jobs)
            print(f"   📊 Average quality score: {avg_quality:.1f}/10")
            
            # Show unique companies found
            companies = list(set(job.get('company', 'Unknown') for job in jobs))
            print(f"   🏢 Companies found: {', '.join(companies)}")
            
            # Show job sources/platforms
            sources = list(set(job.get('source', 'Unknown') for job in jobs))
            print(f"   📋 Job platforms: {', '.join(sources)}")
        
        # Display top 3 jobs
        print(f"\n🏆 TOP 3 JOB OPPORTUNITIES:")
        print("-" * 60)
        
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n#{i}. {job.get('title', 'Unknown Title')}")
            print(f"   🏢 Company: {job.get('company', 'Unknown')}")
            print(f"   🔗 URL: {job.get('url', 'No URL')}")
            print(f"   📊 Quality Score: {job.get('quality_score', 0):.1f}/10")
            print(f"   📍 Source: {job.get('source', 'Unknown')}")
            
            # Show AI summary (truncated)
            ai_summary = job.get('ai_summary', 'No AI summary available')
            if len(ai_summary) > 200:
                ai_summary = ai_summary[:200] + "..."
            print(f"   🤖 AI Summary: {ai_summary}")
        
        # Save results to file
        output_file = save_enhanced_results_to_file(jobs, job_title)
        print(f"\n💾 RESULTS SAVED TO FILE:")
        print(f"   📄 Filename: {output_file}")
        print(f"   📊 Total jobs: {len(jobs)}")
        print(f"   🔗 Ready for applications!")
        
        # Compare to your successful example
        print(f"\n🎯 COMPARISON TO YOUR SUCCESSFUL EXAMPLE:")
        print(f"   📊 Your results: 48 real job application links")
        print(f"   📊 This run: {len(jobs)} enhanced job opportunities")
        print(f"   🚀 Success rate: {'High' if len(jobs) >= 3 else 'Moderate'}")
        print(f"   ✨ Enhanced features: AI summaries, quality scores, smart filtering")
        
    except Exception as e:
        print(f"❌ Enhanced job search failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 80)
    print("✅ Enhanced job search completed!")
    print("\n💡 KEY ENHANCEMENTS ADDED TO YOUR PROVEN APPROACH:")
    print("   🤖 LangChain integration for AI-powered job summaries")
    print("   🎯 Refined search queries targeting specific job boards")
    print("   🔍 Smart filtering for real application links")
    print("   ⭐ Quality scoring and ranking system")
    print("   📊 Enhanced company name extraction")
    print("   💾 Structured file export with detailed information")
    print("\n🔗 Based on your successful techniques that found jobs at:")
    print("   🏢 Databricks, Mistral AI, Samsara, xAI, Outschool, SentinelOne, etc.")

if __name__ == "__main__":
    main() 