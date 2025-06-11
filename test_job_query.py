#!/usr/bin/env python3
"""
🧪 TEST JOB SEARCH QUERY FORMATS

Test different query formats to see which ones work with the Google Custom Search API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_job_queries():
    """Test different job search query formats"""
    
    api_key = os.getenv("API_KEY")
    cse_id = os.getenv("CSE_ID")
    url = "https://www.googleapis.com/customsearch/v1"
    
    # Test different query formats
    test_queries = [
        "SDET jobs",                           # Simple format
        "SDET Chicago jobs",                   # Location integrated  
        "SDET jobs in Chicago",               # Original failing format
        "Software Engineer jobs",              # Different role
        "test automation engineer jobs",       # Lower case
        "python developer remote jobs"        # Remote jobs
    ]
    
    print("🧪 Testing Different Job Query Formats")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": 3
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"   📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                print(f"   ✅ Success! Found {len(items)} results")
                
                # Show first result
                if items:
                    first = items[0]
                    print(f"   📝 Sample: {first.get('title', 'N/A')[:50]}...")
                    
            else:
                print(f"   ❌ Failed: {response.status_code}")
                error_data = response.json() if response.text else {"error": "No response"}
                print(f"   💥 Error: {error_data.get('error', {}).get('message', 'Unknown')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_job_queries() 