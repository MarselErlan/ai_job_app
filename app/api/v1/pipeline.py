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
def start_pipeline(request: PipelineRequest):
    """
    🚀 Standard Pipeline Execution
    
    Runs the original pipeline with persistent job search and basic automation.
    Reliable and battle-tested for consistent job applications.
    """
    file_path = os.path.join("uploads", request.resume_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")

    logger.info(f"🚀 Starting standard pipeline for {request.name}")
    
    result = run_pipeline(
        file_path=file_path,
        name=request.name,
        email=request.email,
        phone=request.phone,
        role=request.role,
        location=request.location
    )
    return result

@router.post("/enhanced")
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
    file_path = os.path.join("uploads", request.resume_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")

    logger.info(f"✨ Starting Enhanced Pipeline V5 for {request.name}")
    logger.info(f"🧠 AI Features: {'Enabled' if request.enable_ai_features else 'Disabled'}")
    
    try:
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
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Enhanced pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced pipeline execution failed: {str(e)}")

@router.post("/apply-multi")
def apply_to_multiple_jobs(request: PipelineRequest):
    """
    🎯 Multi-Apply Pipeline (Enhanced Implementation)
    
    Applies to multiple jobs using the enhanced pipeline with intelligent
    job selection and optimization for each application.
    
    This is a new implementation using the enhanced V5 pipeline to find
    and apply to the best matching jobs with AI-powered optimization.
    """
    file_path = os.path.join("uploads", request.resume_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")

    logger.info(f"🎯 Starting Multi-Apply Enhanced Pipeline for {request.name}")
    
    try:
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
            
            # Provide recommendations for future applications
            if result.get("resume_optimization"):
                optimization_score = result["resume_optimization"].get("optimization_score", 0)
                if optimization_score > 0.8:
                    result["recommendation"] = "Excellent resume optimization! Consider applying to more premium positions."
                elif optimization_score > 0.6:
                    result["recommendation"] = "Good optimization. Consider targeting similar companies."
                else:
                    result["recommendation"] = "Resume could be improved. Review suggested changes."
        
        result["api_version"] = "v5.0-multi"
        result["endpoint"] = "/api/v1/pipeline/apply-multi"
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Multi-apply pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Multi-apply pipeline execution failed: {str(e)}")

@router.get("/status")
def get_pipeline_status():
    """
    📊 Pipeline Status and Capabilities
    
    Returns information about available pipeline versions and their capabilities.
    """
    try:
        # Check if enhanced pipeline is available
        pipeline = EnhancedPipelineV5()
        ai_available = pipeline.llm is not None
        
        return {
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
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "standard_pipeline_available": True,
            "enhanced_pipeline_available": False
        }

@router.get("/health")
def health_check():
    """
    🏥 Pipeline Health Check
    
    Simple health check endpoint for monitoring and load balancers.
    """
    return {
        "status": "healthy",
        "service": "AI Job Application Pipeline",
        "version": "5.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

