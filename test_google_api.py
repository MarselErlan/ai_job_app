#!/usr/bin/env python3
"""
🔍 GOOGLE CUSTOM SEARCH API DEBUGGING SCRIPT

This script helps debug Google Custom Search API configuration issues
by testing different request formats and providing detailed error analysis.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_google_api():
    """Test Google Custom Search API with different configurations"""
    
    # Get credentials from environment (using the same names as job_scraper.py)
    api_key = os.getenv("API_KEY")
    cse_id = os.getenv("CSE_ID")
    
    print("🔍 Testing Google Custom Search API Configuration")
    print("=" * 60)
    
    # Check if credentials are loaded
    print(f"🔑 API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"🆔 CSE ID: {'✅ Set' if cse_id else '❌ Missing'}")
    
    if not api_key or not cse_id:
        print("\n❌ Missing required credentials!")
        print("Please check your .env file contains:")
        print("API_KEY=your_api_key_here")
        print("CSE_ID=your_cse_id_here")
        return False
    
    # Test 1: Simple search request
    print(f"\n🧪 Test 1: Basic API connectivity")
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": "test",
        "num": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"📡 Status Code: {response.status_code}")
        print(f"📏 Response Size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Working! Sample result:")
            if "items" in data and len(data["items"]) > 0:
                first_item = data["items"][0]
                print(f"   📝 Title: {first_item.get('title', 'N/A')}")
                print(f"   🔗 URL: {first_item.get('link', 'N/A')}")
            return True
        else:
            print("❌ API Error:")
            try:
                error_data = response.json()
                print(f"   💥 Error: {error_data}")
                
                # Common error analysis
                if response.status_code == 400:
                    print("\n🔍 Analysis: 400 Bad Request")
                    print("   Possible causes:")
                    print("   1. Invalid API key format")
                    print("   2. Invalid Custom Search Engine ID")
                    print("   3. CSE not configured properly")
                    print("   4. API key doesn't have Custom Search API enabled")
                    
                elif response.status_code == 403:
                    print("\n🔍 Analysis: 403 Forbidden")
                    print("   Possible causes:")
                    print("   1. API key is valid but Custom Search API not enabled")
                    print("   2. Billing not set up for Google Cloud project")
                    print("   3. Daily quota exceeded")
                    
            except:
                print(f"   Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False
    
    # Test 2: Check if it's a CSE configuration issue
    print(f"\n🧪 Test 2: CSE Configuration Check")
    
    # Try with a different, simpler query
    params["q"] = "python"
    params["num"] = 3
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            print("✅ CSE appears to be working with simple queries")
        else:
            print("❌ CSE configuration issue detected")
            
    except Exception as e:
        print(f"❌ CSE test failed: {e}")
    
    return False

def suggest_fixes():
    """Provide specific fix suggestions based on common issues"""
    print("\n🛠️ COMMON FIXES:")
    print("=" * 60)
    
    print("1. 🔑 API Key Issues:")
    print("   - Go to Google Cloud Console")
    print("   - Enable 'Custom Search API'")
    print("   - Create new API key if current one is invalid")
    print("   - Check API key restrictions")
    
    print("\n2. 🆔 Custom Search Engine Issues:")
    print("   - Go to https://cse.google.com/")
    print("   - Create new Custom Search Engine")
    print("   - Set 'Search the entire web' option")
    print("   - Copy the correct CSE ID")
    
    print("\n3. 📋 .env File Fix:")
    print("   API_KEY=your_actual_api_key")
    print("   CSE_ID=your_actual_cse_id")
    
    print("\n4. 🧪 Alternative Test (using curl):")
    api_key = os.getenv("API_KEY", "YOUR_API_KEY")
    cse_id = os.getenv("CSE_ID", "YOUR_CSE_ID")
    
    curl_command = f"""curl -X GET \\
  "https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q=test&num=1" \\
  -H "Accept: application/json"
"""
    print(curl_command)

if __name__ == "__main__":
    print("🚀 Starting Google API Debug Test")
    
    success = test_google_api()
    
    if not success:
        suggest_fixes()
    else:
        print("\n🎉 Google API is working correctly!")
        print("The issue might be in the job scraper implementation.") 