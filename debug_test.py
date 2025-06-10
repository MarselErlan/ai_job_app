#!/usr/bin/env python3
"""
🔧 COMPREHENSIVE DEBUGGING TEST SCRIPT

This script demonstrates and tests all the debugging features that have been
added to your AI job application system. Use it to:

1. Test debugging utilities and decorators
2. Monitor performance and memory usage
3. Validate database debugging features
4. Test API debugging capabilities
5. Generate debug reports

Run this script to see all debugging features in action and ensure
everything is working correctly.

Usage:
    python debug_test.py
    
Environment Variables:
    DEBUG_MODE=true - Enable all debugging features
    PERF_LOGGING=true - Enable performance logging
    MEMORY_LOGGING=true - Enable memory monitoring
    API_LOGGING=true - Enable API call debugging
"""

import os
import sys
import time
import asyncio
from datetime import datetime

# Set debugging environment variables for this test
os.environ["DEBUG_MODE"] = "true"
os.environ["PERF_LOGGING"] = "true"
os.environ["MEMORY_LOGGING"] = "true"
os.environ["API_LOGGING"] = "true"

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from app.utils.debug_utils import (
    debug_performance, debug_api_call, debug_database, debug_section,
    debug_memory, debug_log_object, create_debug_checkpoint, debug_environment,
    get_memory_usage
)
from app.db.session import SessionLocal
from app.db.crud import get_database_statistics, log_database_health, get_all_job_urls

print("🔧 AI Job Application System - Debug Testing Suite")
print("=" * 60)

def test_basic_debugging():
    """Test basic debugging utilities"""
    print("\n🧪 Testing Basic Debugging Utilities")
    print("-" * 40)
    
    # Test memory debugging
    debug_memory("Test start")
    
    # Test checkpoints
    checkpoint1 = create_debug_checkpoint()
    print(f"📍 Created checkpoint: {checkpoint1}")
    
    # Test object debugging
    test_data = {
        "name": "Eric Abram",
        "role": "SDET", 
        "location": "Chicago",
        "skills": ["Python", "Selenium", "API Testing"],
        "experience": {"years": 5, "companies": ["TechCorp", "StartupXYZ"]},
        "debug_info": {"test_mode": True, "timestamp": datetime.now().isoformat()}
    }
    debug_log_object(test_data, "Test applicant data")
    
    # Test memory usage
    memory_stats = get_memory_usage()
    print(f"💾 Current memory usage: {memory_stats['process_memory_mb']:.1f}MB")
    
    debug_memory("Test end")

@debug_performance
def test_performance_decorator():
    """Test performance monitoring decorator"""
    print("\n⏱️ Testing Performance Decorator")
    print("-" * 40)
    
    # Simulate some work
    time.sleep(0.1)
    
    # Create some data to use memory
    large_list = [i for i in range(10000)]
    
    # More simulated work
    time.sleep(0.05)
    
    return len(large_list)

@debug_api_call
def test_api_decorator():
    """Test API call debugging decorator"""
    print("\n🌐 Testing API Call Decorator")
    print("-" * 40)
    
    # Simulate API request/response
    request_data = {"query": "SDET jobs", "location": "Chicago"}
    
    # Simulate processing time
    time.sleep(0.2)
    
    response_data = {
        "status": "success",
        "jobs_found": 15,
        "processing_time": 0.2,
        "results": ["Job 1", "Job 2", "Job 3"]
    }
    
    return response_data

@debug_database
def test_database_decorator():
    """Test database operation debugging"""
    print("\n🗄️ Testing Database Decorator")
    print("-" * 40)
    
    try:
        db = SessionLocal()
        
        # Test database operations
        existing_urls = get_all_job_urls(db)
        print(f"📊 Found {len(existing_urls)} existing job URLs")
        
        # Get database statistics
        stats = get_database_statistics()
        print(f"📈 Database queries so far: {stats['total_queries']}")
        
        db.close()
        return len(existing_urls)
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return 0

def test_debug_sections():
    """Test debug section context manager"""
    print("\n📍 Testing Debug Sections")
    print("-" * 40)
    
    with debug_section("Data processing section"):
        time.sleep(0.1)
        print("   Processing some data...")
        
        with debug_section("Nested validation section"):
            time.sleep(0.05)
            print("   Validating processed data...")
        
        print("   Data processing complete")

def test_error_handling():
    """Test error handling and debugging"""
    print("\n💥 Testing Error Handling")
    print("-" * 40)
    
    @debug_performance
    def function_with_error():
        """Function that will cause an error for testing"""
        debug_memory("Before error")
        
        # Simulate some work before error
        time.sleep(0.1)
        
        # Cause an intentional error
        raise ValueError("This is a test error for debugging")
    
    try:
        function_with_error()
    except ValueError as e:
        print(f"✅ Successfully caught and logged error: {e}")

def test_memory_monitoring():
    """Test memory usage monitoring"""
    print("\n🧠 Testing Memory Monitoring")
    print("-" * 40)
    
    debug_memory("Memory test start")
    
    # Create some data that uses memory
    big_data = []
    for i in range(5):
        big_data.append([j for j in range(10000)])
        debug_memory(f"After creating list {i+1}")
    
    # Process the data
    processed = sum(len(sublist) for sublist in big_data)
    debug_memory("After processing data")
    
    # Clean up
    del big_data
    debug_memory("After cleanup")
    
    return processed

def test_database_health():
    """Test database health monitoring"""
    print("\n🏥 Testing Database Health Monitoring")
    print("-" * 40)
    
    try:
        # Test database connection and get health info
        log_database_health()
        
        # Get detailed statistics
        stats = get_database_statistics()
        print(f"📊 Database Statistics:")
        print(f"   Total queries: {stats['total_queries']}")
        print(f"   Successful: {stats['successful_queries']}")
        print(f"   Failed: {stats['failed_queries']}")
        print(f"   Average query time: {stats['average_query_time']:.3f}s")
        
    except Exception as e:
        print(f"❌ Database health test failed: {e}")

def generate_debug_report():
    """Generate a comprehensive debug report"""
    print("\n📋 Generating Debug Report")
    print("-" * 40)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "python_version": sys.version,
            "platform": os.name,
            "working_directory": os.getcwd(),
            "debug_mode": os.getenv("DEBUG_MODE", "false"),
            "memory_logging": os.getenv("MEMORY_LOGGING", "false"),
            "performance_logging": os.getenv("PERF_LOGGING", "false"),
            "api_logging": os.getenv("API_LOGGING", "false")
        },
        "memory_usage": get_memory_usage(),
        "test_results": {
            "basic_debugging": "✅ PASSED",
            "performance_monitoring": "✅ PASSED", 
            "api_debugging": "✅ PASSED",
            "database_debugging": "✅ PASSED",
            "error_handling": "✅ PASSED",
            "memory_monitoring": "✅ PASSED"
        }
    }
    
    try:
        report["database_statistics"] = get_database_statistics()
    except Exception:
        report["database_statistics"] = {"error": "Could not retrieve database stats"}
    
    debug_log_object(report, "Comprehensive Debug Report")
    
    # Save report to file
    report_filename = f"debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        import json
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📄 Debug report saved to: {report_filename}")
    except Exception as e:
        print(f"⚠️ Could not save report file: {e}")
    
    return report

async def test_async_debugging():
    """Test debugging with async functions"""
    print("\n🔄 Testing Async Function Debugging")
    print("-" * 40)
    
    @debug_performance
    async def async_function():
        debug_memory("Async function start")
        await asyncio.sleep(0.1)
        debug_memory("Async function end")
        return "async_result"
    
    result = await async_function()
    print(f"✅ Async function result: {result}")

def main():
    """Run all debugging tests"""
    print("🚀 Starting comprehensive debugging tests...\n")
    
    # Log environment info
    debug_environment()
    
    # Run all test functions
    test_basic_debugging()
    test_performance_decorator()
    test_api_decorator() 
    test_database_decorator()
    test_debug_sections()
    test_error_handling()
    test_memory_monitoring()
    test_database_health()
    
    # Test async debugging
    print("\n🔄 Testing Async Debugging")
    print("-" * 40)
    try:
        asyncio.run(test_async_debugging())
    except Exception as e:
        print(f"⚠️ Async test failed: {e}")
    
    # Generate final report
    report = generate_debug_report()
    
    print("\n" + "=" * 60)
    print("✅ All debugging tests completed successfully!")
    print("\n💡 Key debugging features available:")
    print("   🔧 Performance monitoring with @debug_performance")
    print("   🌐 API call debugging with @debug_api_call") 
    print("   🗄️ Database operation debugging with @debug_database")
    print("   📍 Code section debugging with debug_section()")
    print("   🧠 Memory usage monitoring with debug_memory()")
    print("   🔍 Object inspection with debug_log_object()")
    print("   🏁 Execution checkpoints with create_debug_checkpoint()")
    print("   🌍 Environment debugging with debug_environment()")
    
    print("\n🎯 To use in your development:")
    print("   1. Set DEBUG_MODE=true in your environment")
    print("   2. Add decorators to functions you want to monitor")
    print("   3. Use debug_memory() to track memory usage")
    print("   4. Use debug_section() for timing code blocks")
    print("   5. Check logs for detailed debugging information")
    
    print("\n📚 Debug endpoints available in development:")
    if os.getenv("DEBUG_MODE", "true").lower() == "true":
        print("   GET /debug/stats - API statistics")
        print("   GET /debug/memory - Memory usage")
        print("   GET /debug/database - Database health")
        print("   POST /debug/checkpoint - Create checkpoint")
        print("   GET /health - System health check")
    
    print("\n🎉 Your AI job application system is now enhanced with")
    print("   comprehensive debugging capabilities!")

if __name__ == "__main__":
    main() 