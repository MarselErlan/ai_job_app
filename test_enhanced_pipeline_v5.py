#!/usr/bin/env python3
"""
Test Enhanced Pipeline V5 with LangChain Integration

This script tests the new enhanced pipeline to ensure all features work correctly:
- LangChain AI integration
- Advanced job search strategies  
- Intelligent resume tailoring
- Enhanced form automation
- Comprehensive analytics

Usage:
    python test_enhanced_pipeline_v5.py
"""

import sys
import os
import json
from pathlib import Path
from loguru import logger

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

def test_enhanced_pipeline_imports():
    """Test that all enhanced pipeline components can be imported"""
    logger.info("🔧 Testing Enhanced Pipeline V5 imports...")
    
    try:
        from app.tasks.pipeline_for_5 import (
            EnhancedPipelineV5,
            run_enhanced_pipeline_v5_sync,
            generate_advanced_search_strategies,
            advanced_resume_tailoring,
            enhanced_persistent_job_search
        )
        logger.success("✅ All enhanced pipeline imports successful")
        return True
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_langchain_availability():
    """Test if LangChain is available and working"""
    logger.info("🧠 Testing LangChain availability...")
    
    try:
        from app.tasks.pipeline_for_5 import LANGCHAIN_AVAILABLE
        if LANGCHAIN_AVAILABLE:
            logger.success("✅ LangChain is available and ready")
            return True
        else:
            logger.warning("⚠️ LangChain not available - enhanced features will be disabled")
            return False
    except Exception as e:
        logger.error(f"❌ LangChain test failed: {e}")
        return False

def test_enhanced_pipeline_initialization():
    """Test enhanced pipeline initialization"""
    logger.info("🚀 Testing Enhanced Pipeline V5 initialization...")
    
    try:
        from app.tasks.pipeline_for_5 import EnhancedPipelineV5
        
        pipeline = EnhancedPipelineV5()
        logger.info(f"📝 Pipeline checkpoint: {pipeline.checkpoint_id}")
        logger.info(f"🧠 LLM initialized: {pipeline.llm is not None}")
        logger.info(f"💭 Memory initialized: {pipeline.memory is not None}")
        logger.info(f"🔍 Job analyzer: {pipeline.job_analyzer is not None}")
        logger.info(f"📄 Resume optimizer: {pipeline.resume_optimizer is not None}")
        
        logger.success("✅ Enhanced Pipeline V5 initialization successful")
        return True
    except Exception as e:
        logger.error(f"❌ Pipeline initialization failed: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints can be imported and configured"""
    logger.info("🌐 Testing Enhanced API endpoints...")
    
    try:
        from app.api.v1.pipeline import router
        logger.info(f"📡 API router configured with routes:")
        
        for route in router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                logger.info(f"   {list(route.methods)[0] if route.methods else 'GET'} {route.path}")
        
        logger.success("✅ Enhanced API endpoints configured successfully")
        return True
    except Exception as e:
        logger.error(f"❌ API endpoint test failed: {e}")
        return False

def test_enhanced_search_strategies():
    """Test enhanced search strategy generation"""
    logger.info("🎯 Testing enhanced search strategy generation...")
    
    try:
        from app.tasks.pipeline_for_5 import EnhancedPipelineV5, generate_advanced_search_strategies
        
        pipeline = EnhancedPipelineV5()
        strategies = generate_advanced_search_strategies("SDET", "Chicago", pipeline)
        
        logger.info(f"📊 Generated {len(strategies)} search strategies:")
        for i, strategy in enumerate(strategies[:3], 1):
            logger.info(f"   {i}. {strategy.get('description', 'Unknown')}")
            logger.info(f"      Query: '{strategy.get('query', 'N/A')}' Location: '{strategy.get('location', 'N/A')}'")
            logger.info(f"      Priority: {strategy.get('priority', 0)}")
        
        logger.success("✅ Enhanced search strategy generation successful")
        return True
    except Exception as e:
        logger.error(f"❌ Search strategy test failed: {e}")
        return False

def test_mock_resume_processing():
    """Test resume processing with mock data"""
    logger.info("📄 Testing mock resume processing...")
    
    try:
        # Create mock resume text
        mock_resume = """
        Eric Abram
        Software Development Engineer in Test
        
        EXPERIENCE:
        - 5+ years of test automation experience
        - Python, Selenium, pytest expertise
        - CI/CD pipeline development
        - API testing and performance testing
        
        SKILLS:
        - Python, Java, JavaScript
        - Selenium WebDriver, Playwright
        - Docker, Kubernetes
        - AWS, Jenkins, Git
        """
        
        # Mock job data
        mock_job = {
            "title": "Senior SDET - Test Automation",
            "company": "TechCorp",
            "snippet": "Looking for experienced SDET with Python and Selenium expertise",
            "url": "https://example.com/job/123"
        }
        
        from app.tasks.pipeline_for_5 import EnhancedPipelineV5, advanced_resume_tailoring
        
        pipeline = EnhancedPipelineV5()
        result = advanced_resume_tailoring(mock_resume, mock_job, pipeline)
        
        logger.info("📊 Resume tailoring result:")
        logger.info(f"   Optimization Score: {result.get('optimization_score', 0):.2%}")
        logger.info(f"   ATS Score: {result.get('ats_score', 0):.2%}")
        logger.info(f"   Changes Made: {len(result.get('changes_made', []))}")
        logger.info(f"   Content Length: {len(result.get('content', ''))}")
        
        logger.success("✅ Mock resume processing successful")
        return True
    except Exception as e:
        logger.error(f"❌ Resume processing test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    logger.info("🚀 Starting Enhanced Pipeline V5 Comprehensive Test Suite")
    logger.info("=" * 60)
    
    tests = [
        ("Enhanced Pipeline Imports", test_enhanced_pipeline_imports),
        ("LangChain Availability", test_langchain_availability),
        ("Pipeline Initialization", test_enhanced_pipeline_initialization),
        ("API Endpoints", test_api_endpoints),
        ("Search Strategy Generation", test_enhanced_search_strategies),
        ("Mock Resume Processing", test_mock_resume_processing),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running: {test_name}")
        logger.info("-" * 40)
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    logger.info("-" * 60)
    logger.info(f"📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.success("🌟 All tests passed! Enhanced Pipeline V5 is ready!")
    elif passed >= total * 0.8:
        logger.warning("⚠️ Most tests passed, but some issues detected.")
    else:
        logger.error("❌ Multiple test failures detected. Please review errors above.")
    
    return passed == total

if __name__ == "__main__":
    # Configure logging for test output
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="DEBUG"
    )
    
    # Run the comprehensive test
    success = run_comprehensive_test()
    
    if success:
        logger.info("\n🎯 Next Steps:")
        logger.info("1. Start the server: uvicorn app.main:app --reload")
        logger.info("2. Test enhanced endpoint: POST /api/v1/pipeline/enhanced")
        logger.info("3. Check AI features: GET /api/v1/pipeline/status")
        sys.exit(0)
    else:
        logger.error("\n❌ Please fix the issues above before using Enhanced Pipeline V5")
        sys.exit(1) 