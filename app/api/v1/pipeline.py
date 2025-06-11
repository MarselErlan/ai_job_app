# File: app/api/v1/pipeline.py
"""
PIPELINE API ENDPOINTS - Web interface for running job application pipelines

This module provides HTTP API endpoints for triggering different versions of
the job application pipeline through simple POST requests.

Endpoints:
- POST /api/v1/pipeline/start           : Standard pipeline for single best match
- POST /api/v1/pipeline/enhanced        : Enhanced V5 pipeline with LangChain AI
- POST /api/v1/pipeline/apply-multi     : Multi-apply pipeline (legacy support)

Enhanced V5 Pipeline Features:
- LangChain AI integration for intelligent job analysis
- Advanced resume optimization with ATS scoring
- Smart search strategy generation
- Company culture and salary insights
- Success probability predictions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from loguru import logger
from app.utils.debug_utils import debug_performance

# Configure Loguru
logger.add(
    "logs/pipeline_api.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
)

# Import pipeline functions
from app.tasks.pipeline import run_pipeline
from app.tasks.pipeline_for_5 import (
    run_enhanced_pipeline_v5_sync,
    EnhancedPipelineV5
)

# Create a router for pipeline-related endpoints
router = APIRouter()

# Request models for pipeline execution
class PipelineRequest(BaseModel):
    resume_filename: str
    name: str
    email: str
    phone: str
    role: str
    location: str

class EnhancedPipelineRequest(BaseModel):
    resume_filename: str
    name: str
    email: str
    phone: str
    role: str
    location: str
    enable_ai_features: Optional[bool] = True

@router.post("/start")
@debug_performance
def start_pipeline(request: PipelineRequest):
    """
    🚀 Standard Pipeline Execution
    
    Runs the original pipeline with persistent job search and basic automation.
    Reliable and battle-tested for consistent job applications.
    """
    logger.info(f"🚀 Starting standard pipeline for {request.name}")
    logger.debug(f"Role: {request.role}, Location: {request.location}")
    
    file_path = os.path.join("uploads", request.resume_filename)
    logger.debug(f"Resume file path: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"Resume file not found: {file_path}")
        raise HTTPException(status_code=404, detail="Resume file not found")

    try:
        logger.debug("Executing standard pipeline")
        result = run_pipeline(
            file_path=file_path,
            name=request.name,
            email=request.email,
            phone=request.phone,
            role=request.role,
            location=request.location
        )
        logger.info("Standard pipeline completed successfully")
        logger.debug(f"Pipeline result status: {result.get('status', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"❌ Standard pipeline failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@router.post("/enhanced")
@debug_performance
def start_enhanced_pipeline(request: EnhancedPipelineRequest):
    """
    ✨ Enhanced Pipeline V5 Execution with LangChain AI
    
    Runs the next-generation pipeline with advanced AI features:
    - LangChain agents for intelligent job analysis
    - Multi-agent resume optimization 
    - AI-powered search strategy generation
    - Company culture and salary insights
    - Success probability predictions
    - Advanced ATS optimization
    """
    logger.info(f"✨ Starting Enhanced Pipeline V5 for {request.name}")
    logger.debug(f"Role: {request.role}, Location: {request.location}")
    logger.info(f"🧠 AI Features: {'Enabled' if request.enable_ai_features else 'Disabled'}")
    
    file_path = os.path.join("uploads", request.resume_filename)
    logger.debug(f"Resume file path: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"Resume file not found: {file_path}")
        raise HTTPException(status_code=404, detail="Resume file not found")

    try:
        logger.debug("Executing enhanced pipeline V5")
        result = run_enhanced_pipeline_v5_sync(
            file_path=file_path,
            name=request.name,
            email=request.email,
            phone=request.phone,
            role=request.role,
            location=request.location,
            enable_ai_features=request.enable_ai_features
        )
        
        # Add API-specific metadata
        result["api_version"] = "v5.0"
        result["endpoint"] = "/api/v1/pipeline/enhanced"
        
        logger.info("Enhanced pipeline V5 completed successfully")
        logger.debug(f"Pipeline result: {result.get('status', 'unknown')}, AI insights: {bool(result.get('ai_insights'))}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Enhanced pipeline failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Enhanced pipeline execution failed: {str(e)}")

@router.post("/apply-multi")
@debug_performance
def apply_to_multiple_jobs(request: PipelineRequest):
    """
    🎯 Multi-Apply Pipeline (Enhanced Implementation)
    
    Applies to multiple jobs using the enhanced pipeline with intelligent
    job selection and optimization for each application.
    
    This is a new implementation using the enhanced V5 pipeline to find
    and apply to the best matching jobs with AI-powered optimization.
    """
    logger.info(f"🎯 Starting Multi-Apply Enhanced Pipeline for {request.name}")
    logger.debug(f"Role: {request.role}, Location: {request.location}")
    
    file_path = os.path.join("uploads", request.resume_filename)
    logger.debug(f"Resume file path: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"Resume file not found: {file_path}")
        raise HTTPException(status_code=404, detail="Resume file not found")

    try:
        logger.debug("Executing multi-apply pipeline with AI features enabled")
        # Use enhanced pipeline which finds multiple high-quality jobs
        result = run_enhanced_pipeline_v5_sync(
            file_path=file_path,
            name=request.name,
            email=request.email,
            phone=request.phone,
            role=request.role,
            location=request.location,
            enable_ai_features=True  # Always enable AI for multi-apply
        )
        
        # Add multi-apply specific metadata
        if result.get("status") == "success":
            result["multi_apply_mode"] = True
            result["jobs_analyzed"] = result.get("search_stats", {}).get("analyzed_jobs", 0)
            result["ai_insights_available"] = bool(result.get("best_job", {}).get("ai_analysis"))
            
            logger.info(f"Successfully analyzed {result['jobs_analyzed']} jobs")
            logger.debug(f"AI insights available: {result['ai_insights_available']}")
            
            # Provide recommendations for future applications
            if result.get("resume_optimization"):
                optimization_score = result["resume_optimization"].get("optimization_score", 0)
                logger.debug(f"Resume optimization score: {optimization_score}")
                
                if optimization_score > 0.8:
                    result["recommendation"] = "Excellent resume optimization! Consider applying to more premium positions."
                elif optimization_score > 0.6:
                    result["recommendation"] = "Good optimization. Consider targeting similar companies."
                else:
                    result["recommendation"] = "Resume could be improved. Review suggested changes."
                
                logger.info(f"Generated recommendation based on optimization score: {optimization_score:.2f}")
        
        result["api_version"] = "v5.0-multi"
        result["endpoint"] = "/api/v1/pipeline/apply-multi"
        
        logger.info("Multi-apply pipeline completed successfully")
        logger.debug(f"Final result status: {result.get('status', 'unknown')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Multi-apply pipeline failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Multi-apply pipeline execution failed: {str(e)}")

@router.get("/status")
@debug_performance
def get_pipeline_status():
    """
    📊 Pipeline Status and Capabilities
    
    Returns information about available pipeline versions and their capabilities.
    """
    logger.info("Checking pipeline status and capabilities")
    
    try:
        # Check if enhanced pipeline is available
        logger.debug("Checking enhanced pipeline availability")
        pipeline = EnhancedPipelineV5()
        ai_available = pipeline.llm is not None
        logger.info(f"Enhanced pipeline AI features available: {ai_available}")
        
        status_info = {
            "status": "operational",
            "versions": {
                "standard": {
                    "version": "4.0",
                    "available": True,
                    "features": [
                        "Persistent job search",
                        "Resume tailoring",
                        "Automated form filling",
                        "Database integration",
                        "Notion logging"
                    ]
                },
                "enhanced": {
                    "version": "5.0",
                    "available": True,
                    "ai_features_available": ai_available,
                    "features": [
                        "LangChain AI integration",
                        "Intelligent job analysis",
                        "Multi-agent resume optimization",
                        "ATS scoring and optimization",
                        "Company culture insights",
                        "Success probability predictions",
                        "Advanced search strategies",
                        "Performance analytics"
                    ]
                }
            },
            "endpoints": [
                "/api/v1/pipeline/start",
                "/api/v1/pipeline/enhanced", 
                "/api/v1/pipeline/apply-multi",
                "/api/v1/pipeline/status"
            ]
        }
        
        logger.debug("Successfully compiled pipeline status information")
        return status_info
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {str(e)}", exc_info=True)
        degraded_status = {
            "status": "degraded",
            "error": str(e),
            "standard_pipeline_available": True,
            "enhanced_pipeline_available": False
        }
        logger.warning("Returning degraded status due to error")
        return degraded_status

@router.get("/health")
@debug_performance
def health_check():
    """
    🏥 Pipeline Health Check
    
    Simple health check endpoint for monitoring and load balancers.
    """
    logger.debug("Processing health check request")
    health_status = {
        "status": "healthy",
        "service": "AI Job Application Pipeline",
        "version": "5.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    logger.debug("Health check completed successfully")
    return health_status

