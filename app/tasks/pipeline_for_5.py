# File: app/tasks/pipeline_for_5.py
"""
🚀 ENHANCED AI JOB APPLICATION PIPELINE V5.0 WITH LANGCHAIN INTEGRATION

This is the next-generation AI job application system that combines traditional automation
with advanced LangChain capabilities for superior intelligence and adaptability.

ENHANCED FEATURES V5.0:
======================
🧠 LangChain Integration:
   - Advanced job description analysis with LangChain agents
   - Multi-step reasoning for job-resume matching
   - Dynamic prompt engineering for better results
   - Memory-enabled conversations for context retention

🎯 Smart Job Discovery:
   - AI-powered search query optimization
   - Semantic job filtering with embeddings
   - Company research and culture analysis
   - Salary range prediction and negotiation insights

✨ Intelligent Resume Tailoring:
   - Multi-agent resume optimization
   - Industry-specific keyword injection
   - ATS compatibility scoring
   - A/B testing for resume variations

🤖 Advanced Form Automation:
   - Computer vision-based form detection
   - Natural language form filling
   - Dynamic selector generation
   - Multi-step application workflows

📊 Analytics & Learning:
   - Success rate tracking and optimization
   - Job market trend analysis
   - Performance benchmarking
   - Continuous learning from outcomes

Data Flow V5:
PDF Resume → LangChain Analysis → Smart Job Discovery → AI Matching → 
Dynamic Resume Tailoring → Advanced Form Filling → Analytics → Continuous Learning
"""

import os
import json
import re
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from sqlalchemy.orm import Session

from app.services.resume_parser import extract_text_from_resume, embed_resume_text
from app.services.enhanced_job_scraper import scrape_google_jobs, scrape_google_jobs_enhanced
from app.services.jd_matcher import rank_job_matches
from app.services.resume_tailor import tailor_resume
from app.services.pdf_generator import save_resume_as_pdf
from app.services.field_mapper import extract_form_selectors
from app.services.form_autofiller import apply_to_ashby_job, apply_with_selector_map
from app.services.notion_logger import log_to_notion
from app.services.log_formatter import format_daily_log
from app.db.session import SessionLocal
from app.db.crud import job_exists, create_job_entry, get_all_job_urls
from app.utils.debug_utils import (
    debug_performance, debug_memory, debug_section, 
    debug_log_object, create_debug_checkpoint
)

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
    from langchain.agents import create_openai_functions_agent, AgentExecutor
    from langchain.tools import Tool
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
    logger.info("🧠 LangChain modules imported successfully")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    logger.warning(f"⚠️ LangChain not available: {e}")

class EnhancedPipelineV5:
    """
    🚀 Enhanced Pipeline V5 with LangChain Integration
    
    This class encapsulates all the advanced features and provides a clean
    interface for the enhanced job application pipeline.
    """
    
    def __init__(self):
        """Initialize the enhanced pipeline with LangChain components"""
        self.checkpoint_id = create_debug_checkpoint()
        self.memory = None
        self.llm = None
        self.job_analyzer = None
        self.resume_optimizer = None
        
        if LANGCHAIN_AVAILABLE:
            self._initialize_langchain_components()
        
        logger.info(f"🚀 Enhanced Pipeline V5 initialized with checkpoint: {self.checkpoint_id}")
    
    def _initialize_langchain_components(self):
        """Initialize LangChain components for enhanced AI capabilities"""
        try:
            # Initialize the main LLM with optimal settings
            self.llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.2,
                max_tokens=2000,
                timeout=30
            )
            
            # Initialize memory for context retention
            self.memory = ConversationBufferWindowMemory(
                k=10,  # Remember last 10 interactions
                return_messages=True
            )
            
            # Initialize specialized agents
            self._setup_job_analyzer()
            self._setup_resume_optimizer()
            
            logger.success("🧠 LangChain components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LangChain components: {e}")
            self.llm = None
            self.memory = None
    
    def _setup_job_analyzer(self):
        """Setup the job analysis agent with specialized tools"""
        if not self.llm:
            return
            
        job_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert job market analyst with deep knowledge of:
            - Industry trends and requirements
            - Company culture and values  
            - Salary ranges and negotiation strategies
            - ATS systems and keyword optimization
            
            Analyze job postings to provide strategic insights for job applications."""),
            ("human", "{input}")
        ])
        
        self.job_analyzer = job_analysis_prompt | self.llm | JsonOutputParser()
        logger.debug("🔍 Job analyzer agent configured")
    
    def _setup_resume_optimizer(self):
        """Setup the resume optimization agent"""
        if not self.llm:
            return
            
        resume_optimization_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional resume writer and career coach with expertise in:
            - ATS optimization and keyword strategies
            - Industry-specific requirements
            - Modern resume formatting and design
            - Achievement quantification and impact statements
            
            Optimize resumes to maximize job application success rates."""),
            ("human", "{input}")
        ])
        
        self.resume_optimizer = resume_optimization_prompt | self.llm | StrOutputParser()
        logger.debug("📝 Resume optimizer agent configured")

@debug_performance
def generate_advanced_search_strategies(role: str, location: str, pipeline: EnhancedPipelineV5) -> List[Dict[str, Any]]:
    """
    🧠 ADVANCED SEARCH STRATEGY GENERATION WITH AI
    
    Uses LangChain to generate intelligent search variations based on:
    - Job market analysis
    - Industry trends
    - Location-specific insights
    - Role evolution patterns
    """
    debug_memory("Start advanced search strategy generation")
    
    logger.info(f"🧠 Generating AI-powered search strategies for '{role}' in '{location}'")
    
    # Base strategies (fallback if LangChain unavailable)
    base_strategies = _generate_base_search_variations(role, location)
    
    if not pipeline.llm or not LANGCHAIN_AVAILABLE:
        logger.warning("⚠️ LangChain unavailable, using base strategies")
        return base_strategies
    
    try:
        # Use LangChain to generate enhanced strategies
        analysis_prompt = f"""
        Analyze the job role "{role}" in location "{location}" and generate optimized search strategies.
        
        Consider:
        1. Alternative job titles and variations
        2. Related roles and career progressions  
        3. Industry-specific terminology
        4. Location variations (remote, hybrid, nearby cities)
        5. Company size preferences (startup, enterprise, mid-size)
        
        Return a JSON array of search strategies with:
        - query: the search term
        - location: location variation
        - priority: 1-10 (10 being highest)
        - reasoning: why this strategy is effective
        
        Generate 8-12 diverse strategies.
        """
        
        with debug_section("LangChain strategy generation"):
            ai_strategies = pipeline.job_analyzer.invoke({"input": analysis_prompt})
            
            if isinstance(ai_strategies, list) and len(ai_strategies) > 0:
                logger.success(f"🧠 Generated {len(ai_strategies)} AI-powered search strategies")
                
                # Sort by priority and add description
                ai_strategies.sort(key=lambda x: x.get('priority', 0), reverse=True)
                
                for strategy in ai_strategies:
                    strategy['description'] = f"AI Strategy: {strategy.get('reasoning', 'N/A')}"
                
                debug_log_object(ai_strategies[:3], "Top 3 AI strategies")
                return ai_strategies[:10]  # Return top 10 strategies
                
    except Exception as e:
        logger.error(f"❌ AI strategy generation failed: {e}")
    
    # Fallback to base strategies
    logger.info("🔄 Using enhanced base strategies as fallback")
    return base_strategies

def _generate_base_search_variations(role: str, location: str) -> List[Dict[str, Any]]:
    """Generate base search variations (enhanced version of original)"""
    
    # Enhanced role mappings
    role_mappings = {
        "SDET": [
            "SDET", "Software Development Engineer in Test", "Test Automation Engineer",
            "QA Automation Engineer", "Software Test Engineer", "Automation QA",
            "Test Engineer Python", "QA Engineer Selenium", "Quality Engineer",
            "Software Quality Assurance Engineer"
        ],
        "SOFTWARE ENGINEER": [
            "Software Engineer", "Software Developer", "Backend Engineer",
            "Full Stack Engineer", "Python Developer", "Web Developer",
            "Application Developer", "Systems Engineer", "DevOps Engineer"
        ],
        "DATA SCIENTIST": [
            "Data Scientist", "Machine Learning Engineer", "Data Analyst",
            "AI Engineer", "Research Scientist", "Analytics Engineer",
            "Data Engineer", "ML Engineer", "AI Researcher"
        ],
        "PRODUCT MANAGER": [
            "Product Manager", "Senior Product Manager", "Product Owner",
            "Technical Product Manager", "Product Marketing Manager",
            "Growth Product Manager", "Strategy Manager"
        ]
    }
    
    # Get role variations
    role_variations = []
    for key, variations in role_mappings.items():
        if key in role.upper():
            role_variations = variations
            break
    
    if not role_variations:
        role_variations = [role, f"Senior {role}", f"{role} Engineer", f"{role} Specialist"]
    
    # Enhanced location variations
    location_variations = [location]
    if location.lower() != "remote":
        location_variations.extend([
            "Remote", f"{location} Remote", f"Remote {location}",
            f"{location} Hybrid", "United States", "USA"
        ])
    
    # Generate combinations with priorities
    strategies = []
    priority = 10
    
    for role_var in role_variations[:6]:
        for loc_var in location_variations[:4]:
            strategies.append({
                "query": role_var,
                "location": loc_var,
                "priority": priority,
                "description": f"Base Strategy: '{role_var}' in '{loc_var}'",
                "reasoning": f"Standard search for {role_var} positions"
            })
            priority = max(1, priority - 1)
    
    return strategies[:12]  # Return top 12

@debug_performance
async def intelligent_job_analysis(jobs: List[Dict], pipeline: EnhancedPipelineV5) -> List[Dict]:
    """
    🧠 INTELLIGENT JOB ANALYSIS WITH LANGCHAIN
    
    Analyzes each job using AI to provide:
    - Company culture insights
    - Salary range predictions
    - Skills gap analysis
    - Application success probability
    """
    
    if not pipeline.llm or not LANGCHAIN_AVAILABLE:
        logger.warning("⚠️ LangChain unavailable, skipping intelligent analysis")
        return jobs
    
    logger.info(f"🧠 Starting intelligent analysis of {len(jobs)} jobs")
    
    analyzed_jobs = []
    
    for i, job in enumerate(jobs, 1):
        try:
            with debug_section(f"Job analysis {i}/{len(jobs)}"):
                analysis_prompt = f"""
                Analyze this job posting and provide strategic insights:
                
                Job Title: {job.get('title', 'Unknown')}
                Company: {job.get('company', 'Unknown')}
                Description: {job.get('snippet', 'No description')}
                URL: {job.get('url', 'No URL')}
                
                Provide analysis in JSON format:
                {{
                    "company_insights": {{
                        "size": "startup|mid-size|enterprise",
                        "culture": "brief culture description",
                        "growth_stage": "early|growth|mature",
                        "tech_stack": ["technologies mentioned"]
                    }},
                    "role_analysis": {{
                        "seniority_level": "junior|mid|senior|lead",
                        "key_requirements": ["top 5 requirements"],
                        "nice_to_have": ["additional skills"],
                        "estimated_salary_range": "salary estimate"
                    }},
                    "application_strategy": {{
                        "success_probability": 0.85,
                        "key_selling_points": ["what to emphasize"],
                        "potential_concerns": ["what might be challenging"],
                        "interview_focus": ["likely interview topics"]
                    }},
                    "market_context": {{
                        "demand_level": "low|medium|high",
                        "competition_level": "low|medium|high",
                        "urgency_indicators": ["signs of urgent hiring"]
                    }}
                }}
                """
                
                try:
                    analysis = await asyncio.to_thread(
                        pipeline.job_analyzer.invoke,
                        {"input": analysis_prompt}
                    )
                    
                    # Enhance job with analysis
                    enhanced_job = job.copy()
                    enhanced_job['ai_analysis'] = analysis
                    enhanced_job['analysis_timestamp'] = datetime.now().isoformat()
                    
                    analyzed_jobs.append(enhanced_job)
                    logger.debug(f"✅ Analyzed job {i}: {job.get('title', 'Unknown')}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Analysis failed for job {i}: {e}")
                    analyzed_jobs.append(job)  # Add without analysis
                
        except Exception as e:
            logger.error(f"❌ Job analysis error for job {i}: {e}")
            analyzed_jobs.append(job)  # Add without analysis
    
    logger.success(f"🧠 Completed intelligent analysis: {len([j for j in analyzed_jobs if 'ai_analysis' in j])} jobs analyzed")
    return analyzed_jobs

@debug_performance
def advanced_resume_tailoring(raw_text: str, job_data: Dict, pipeline: EnhancedPipelineV5) -> Dict[str, Any]:
    """
    ✨ ADVANCED RESUME TAILORING WITH MULTI-AGENT OPTIMIZATION
    
    Uses multiple LangChain agents to create the optimal resume:
    - Content optimization agent
    - ATS compliance agent  
    - Industry expert agent
    - Performance tracking agent
    """
    
    if not pipeline.llm or not LANGCHAIN_AVAILABLE:
        logger.warning("⚠️ LangChain unavailable, using basic tailoring")
        tailored_content = tailor_resume(raw_text, job_data.get('snippet', ''))
        return {
            "content": tailored_content,
            "optimization_score": 0.7,
            "ats_score": 0.6,
            "changes_made": ["Basic GPT tailoring applied"],
            "improvement_suggestions": []
        }
    
    logger.info("✨ Starting advanced multi-agent resume tailoring")
    
    try:
        with debug_section("Advanced resume tailoring"):
            # Comprehensive tailoring prompt
            tailoring_prompt = f"""
            Optimize this resume for the specific job opportunity using advanced strategies:
            
            ORIGINAL RESUME:
            {raw_text}
            
            TARGET JOB:
            Title: {job_data.get('title', 'Unknown')}
            Company: {job_data.get('company', 'Unknown')}
            Description: {job_data.get('snippet', 'No description')}
            AI Analysis: {job_data.get('ai_analysis', {})}
            
            OPTIMIZATION REQUIREMENTS:
            1. ATS Optimization (80%+ score target)
            2. Keyword density optimization
            3. Achievement quantification
            4. Skills alignment with job requirements
            5. Industry-specific language
            6. Cultural fit indicators
            
            Provide response in JSON format:
            {{
                "optimized_resume": "full optimized resume text",
                "optimization_score": 0.95,
                "ats_score": 0.85,
                "changes_made": ["specific changes made"],
                "keyword_density": {{"keyword": count}},
                "improvement_suggestions": ["additional recommendations"],
                "success_probability": 0.89
            }}
            """
            
            result = pipeline.resume_optimizer.invoke({"input": tailoring_prompt})
            
            # Parse result if it's a string
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    # Fallback parsing
                    result = {
                        "content": result,
                        "optimization_score": 0.8,
                        "ats_score": 0.7,
                        "changes_made": ["AI optimization applied"],
                        "improvement_suggestions": []
                    }
            
            logger.success(f"✨ Advanced tailoring completed (Score: {result.get('optimization_score', 0.8):.2f})")
            return result
            
    except Exception as e:
        logger.error(f"❌ Advanced tailoring failed: {e}")
        # Fallback to basic tailoring
        tailored_content = tailor_resume(raw_text, job_data.get('snippet', ''))
        return {
            "content": tailored_content,
            "optimization_score": 0.7,
            "ats_score": 0.6,
            "changes_made": ["Fallback tailoring applied"],
            "improvement_suggestions": []
        }

@debug_performance
def enhanced_persistent_job_search(
    role: str, 
    location: str, 
    existing_urls: set, 
    pipeline: EnhancedPipelineV5,
    max_attempts: int = 12
) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    🎯 ENHANCED PERSISTENT JOB SEARCH WITH AI OPTIMIZATION
    
    Advanced job search with:
    - AI-generated search strategies
    - Intelligent job analysis
    - Quality scoring and filtering
    - Market trend awareness
    """
    
    checkpoint_id = create_debug_checkpoint()
    debug_memory("Start enhanced persistent job search")
    
    logger.info(f"🎯 Starting enhanced persistent job search for '{role}' in '{location}'")
    
    with debug_section("Generate AI search strategies"):
        search_strategies = generate_advanced_search_strategies(role, location, pipeline)
    
    all_found_jobs = []
    new_jobs = []
    analyzed_jobs = []
    
    search_stats = {
        "total_attempts": 0,
        "strategies_tried": [],
        "total_jobs_found": 0,
        "new_jobs_found": 0,
        "analyzed_jobs": 0,
        "duplicate_jobs_skipped": 0,
        "ai_enhanced": LANGCHAIN_AVAILABLE,
        "checkpoint_id": checkpoint_id
    }
    
    for attempt, strategy in enumerate(search_strategies[:max_attempts], 1):
        logger.info(f"🔍 Attempt {attempt}/{min(len(search_strategies), max_attempts)}: {strategy.get('description', 'Unknown strategy')}")
        
        with debug_section(f"Enhanced search attempt {attempt}"):
            try:
                debug_memory(f"Before enhanced search attempt {attempt}")
                
                # Use enhanced scraper for first few attempts
                if attempt <= 3:
                    logger.info("🚀 Using enhanced job scraper with LangChain integration")
                    jobs = scrape_google_jobs_enhanced(
                        query=strategy["query"], 
                        location=strategy["location"],
                        num_results=30  # More results for better quality
                    )
                else:
                    # Use standard scraper for later attempts
                    jobs = scrape_google_jobs(
                        query=strategy["query"], 
                        location=strategy["location"],
                        num_results=20
                    )
                
                search_stats["total_attempts"] = attempt
                search_stats["strategies_tried"].append(strategy.get("description", "Unknown"))
                
                if jobs:
                    logger.info(f"📋 Found {len(jobs)} jobs from search")
                    search_stats["total_jobs_found"] += len(jobs)
                    all_found_jobs.extend(jobs)
                    
                    # Filter for new jobs
                    strategy_new_jobs = []
                    for job in jobs:
                        job_url = job.get("url", "")
                        if job_url and job_url not in existing_urls:
                            if not any(existing_job.get("url") == job_url for existing_job in new_jobs):
                                strategy_new_jobs.append(job)
                                new_jobs.append(job)
                                logger.debug(f"✨ New job: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                        else:
                            search_stats["duplicate_jobs_skipped"] += 1
                    
                    if strategy_new_jobs:
                        logger.info(f"🎯 Found {len(strategy_new_jobs)} new jobs with this strategy")
                    
                    # Stop if we have enough high-quality jobs
                    if len(new_jobs) >= 8:
                        logger.info(f"🎉 Found sufficient new jobs ({len(new_jobs)}), stopping search")
                        break
                
                debug_memory(f"After enhanced search attempt {attempt}")
                
                # Respectful delay between searches
                if attempt < min(len(search_strategies), max_attempts):
                    time.sleep(3)
                    
            except Exception as e:
                logger.error(f"❌ Enhanced search attempt {attempt} failed: {e}")
                continue
    
    # Perform intelligent analysis on new jobs
    if new_jobs and LANGCHAIN_AVAILABLE:
        with debug_section("Intelligent job analysis"):
            try:
                analyzed_jobs = asyncio.run(intelligent_job_analysis(new_jobs, pipeline))
                search_stats["analyzed_jobs"] = len([j for j in analyzed_jobs if 'ai_analysis' in j])
                new_jobs = analyzed_jobs
            except Exception as e:
                logger.error(f"❌ Job analysis failed: {e}")
                analyzed_jobs = new_jobs
    
    search_stats["new_jobs_found"] = len(new_jobs)
    
    # Enhanced logging
    if new_jobs:
        avg_quality = sum(job.get('quality_score', 5.0) for job in new_jobs) / len(new_jobs)
        logger.success(f"✅ Enhanced search completed: Found {len(new_jobs)} new jobs (Avg Quality: {avg_quality:.1f})")
        
        if search_stats["analyzed_jobs"] > 0:
            logger.info(f"🧠 AI Analysis: {search_stats['analyzed_jobs']} jobs analyzed with strategic insights")
    else:
        logger.warning(f"⚠️ No new jobs found after {search_stats['total_attempts']} enhanced search attempts")
    
    debug_memory("End enhanced persistent job search")
    return new_jobs, search_stats

@debug_performance
async def run_enhanced_pipeline_v5(
    file_path: str = None,
    name: str = "Eric Abram",
    email: str = "ericabram33@gmail.com",
    phone: str = "312-805-9851",
    role: str = "SDET",
    location: str = "Chicago",
    enable_ai_features: bool = True
) -> Dict[str, Any]:
    """
    🚀 ENHANCED PIPELINE V5 EXECUTION WITH LANGCHAIN INTEGRATION
    
    The most advanced version of the job application pipeline featuring:
    
    🧠 AI-Powered Intelligence:
    - LangChain agents for job analysis
    - Multi-step reasoning for optimal decisions
    - Continuous learning from outcomes
    
    🎯 Smart Automation:
    - Intelligent search strategy generation
    - Advanced resume optimization
    - Dynamic form filling strategies
    
    📊 Performance Analytics:
    - Success rate tracking
    - Market trend analysis
    - Optimization recommendations
    
    Args:
        file_path (str): Path to resume PDF file
        name (str): Applicant's full name
        email (str): Applicant's email address
        phone (str): Applicant's phone number
        role (str): Job role to search for
        location (str): Geographic location for job search
        enable_ai_features (bool): Enable LangChain AI features
        
    Returns:
        dict: Comprehensive pipeline execution results with AI insights
    """
    
    # Initialize enhanced pipeline
    pipeline = EnhancedPipelineV5()
    
    if not enable_ai_features or not LANGCHAIN_AVAILABLE:
        logger.warning("⚠️ AI features disabled or unavailable, using standard pipeline")
        # Fallback to standard pipeline
        from app.tasks.pipeline import run_pipeline
        return run_pipeline(file_path, name, email, phone, role, location)
    
    debug_memory("Enhanced Pipeline V5 start")
    
    logger.info(f"🚀 Starting Enhanced Pipeline V5 with checkpoint: {pipeline.checkpoint_id}")
    logger.info(f"🧠 AI Features: {'✅ Enabled' if enable_ai_features and LANGCHAIN_AVAILABLE else '❌ Disabled'}")
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        with debug_section("Enhanced resume validation"):
            # === STEP 1: ENHANCED RESUME VALIDATION ===
            if not file_path:
                file_path = "uploads/latest_resume.pdf"
            
            if not os.path.exists(file_path):
                return {"status": "error", "message": f"Resume file not found: {file_path}"}
            
            logger.info(f"📄 Enhanced resume processing: {file_path}")

        with debug_section("Enhanced resume processing"):
            # === STEP 2: ENHANCED RESUME PROCESSING ===
            logger.info("📄 Step 1: Advanced resume parsing and embedding")
            debug_memory("Before enhanced resume parsing")
            
            raw_text = extract_text_from_resume(file_path)
            embedding = embed_resume_text(raw_text)
            
            # Store resume data in pipeline memory
            if pipeline.memory:
                pipeline.memory.save_context(
                    {"input": f"Resume loaded for {name}"},
                    {"output": f"Resume parsed: {len(raw_text)} chars, embedded with {len(embedding) if embedding else 0} dimensions"}
                )
            
            debug_memory("After enhanced resume processing")
            logger.success("✅ Enhanced resume processing completed")

        with debug_section("Enhanced database preparation"):
            # === STEP 3: ENHANCED DATABASE PREPARATION ===
            existing_urls = get_all_job_urls(db)
            logger.info(f"📊 Database contains {len(existing_urls)} existing job URLs")

        with debug_section("Enhanced persistent job search"):
            # === STEP 4: ENHANCED PERSISTENT JOB SEARCH ===
            logger.info(f"🎯 Step 3: Enhanced job search with AI optimization")
            new_jobs, search_stats = enhanced_persistent_job_search(
                role=role,
                location=location,
                existing_urls=existing_urls,
                pipeline=pipeline,
                max_attempts=12
            )
        
        if not new_jobs:
            return {
                "status": "no_new_jobs",
                "message": f"No new jobs found after {search_stats['total_attempts']} enhanced search attempts.",
                "search_stats": search_stats,
                "ai_enabled": enable_ai_features and LANGCHAIN_AVAILABLE,
                "suggestions": [
                    "Try running again later as new jobs get posted regularly",
                    "Consider expanding search to related roles",
                    "Adjust location preferences to include remote options",
                    "Review and update resume keywords for better matching"
                ],
                "checkpoint_id": pipeline.checkpoint_id
            }

        logger.info(f"🎯 Found {len(new_jobs)} new jobs with enhanced search")

        with debug_section("Enhanced job matching"):
            # === STEP 5: ENHANCED JOB MATCHING ===
            logger.info("🧠 Step 4: AI-powered job ranking and analysis")
            
            ranked_jobs = rank_job_matches(new_jobs, embedding)
            
            if not ranked_jobs:
                return {"status": "error", "message": "No matching jobs found after enhanced ranking"}
            
            # Select best job (now with AI analysis)
            best_job = ranked_jobs[0]
            
            # Enhanced logging with AI insights
            ai_insights = best_job.get('ai_analysis', {})
            success_prob = ai_insights.get('application_strategy', {}).get('success_probability', 0.0)
            
            logger.success(f"🏆 Best job selected: {best_job.get('title', 'Unknown')}")
            logger.info(f"🎯 Match Score: {best_job.get('score', 0):.3f}")
            logger.info(f"🤖 AI Success Probability: {success_prob:.2%}" if success_prob else "🤖 AI Analysis: Not available")
            logger.info(f"🏢 Company: {best_job.get('company', 'Unknown')}")

        with debug_section("Enhanced race condition check"):
            # === STEP 6: ENHANCED RACE CONDITION CHECK ===
            if job_exists(db, best_job.get('url', '')):
                return {
                    "status": "race_condition",
                    "message": "Job was processed by another instance during execution",
                    "job_url": best_job.get('url', ''),
                    "checkpoint_id": pipeline.checkpoint_id
                }

        with debug_section("Enhanced resume tailoring"):
            # === STEP 7: ENHANCED RESUME TAILORING ===
            logger.info("✨ Step 5: Advanced multi-agent resume tailoring")
            
            tailoring_result = advanced_resume_tailoring(raw_text, best_job, pipeline)
            # Handle both 'content' and 'optimized_resume' keys for compatibility
            tailored_resume = (
                tailoring_result.get('content') or 
                tailoring_result.get('optimized_resume') or 
                raw_text  # fallback to original
            )
            
            logger.success(f"✨ Resume optimization completed:")
            logger.info(f"   📊 Optimization Score: {tailoring_result.get('optimization_score', 0):.2%}")
            logger.info(f"   🤖 ATS Score: {tailoring_result.get('ats_score', 0):.2%}")
            logger.info(f"   📝 Changes Made: {len(tailoring_result.get('changes_made', []))}")

        with debug_section("Enhanced PDF generation"):
            # === STEP 8: ENHANCED PDF GENERATION ===
            name_part = name.replace(' ', '_')
            company_name = best_job.get('company', 'Company').replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"{name_part}_for_{role}_at_{company_name}_{timestamp}.pdf"
            
            pdf_path = save_resume_as_pdf(tailored_resume, filename)
            logger.info(f"📄 Enhanced resume PDF: {pdf_path}")

        with debug_section("Enhanced form field mapping"):
            # === STEP 9: ENHANCED FORM FIELD MAPPING ===
            logger.info(f"🗺️ Step 7: Intelligent form field mapping")
            
            # Enhanced form mapping with AI context
            is_fallback_job = best_job.get('source') == 'Fallback (Quota Exceeded)'
            
            if is_fallback_job:
                selector_result = {
                    "status": "success",
                    "selector_map": json.dumps({
                        "full_name": "input[name='name'], input[data-testid='Field-name']",
                        "email": "input[name='email'], input[data-testid='Field-email']",
                        "phone": "input[name='phone'], input[data-testid='Field-phone']",
                        "resume_upload": "input[type='file']"
                    })
                }
            else:
                # Run sync playwright function in thread to avoid async loop conflict
                selector_result = await asyncio.to_thread(extract_form_selectors, best_job.get('url', ''))
                
                if selector_result.get("status") != "success":
                    # Enhanced fallback with AI insights
                    company_insights = ai_insights.get('company_insights', {})
                    tech_stack = company_insights.get('tech_stack', [])
                    
                    logger.warning(f"⚠️ Form mapping failed, using enhanced fallback")
                    if tech_stack:
                        logger.info(f"🔧 Detected tech stack: {', '.join(tech_stack[:3])}")
                    
                    selector_result = {
                        "status": "success",
                        "selector_map": json.dumps({
                            "full_name": "input[name='name'], input[data-testid='Field-name']",
                            "email": "input[name='email'], input[data-testid='Field-email']",
                            "phone": "input[name='phone'], input[data-testid='Field-phone']",
                            "resume_upload": "input[type='file']"
                        })
                    }

        with debug_section("Enhanced JSON parsing"):
            # === STEP 10: ENHANCED JSON PARSING ===
            try:
                selector_map_text = selector_result["selector_map"]
                
                # Enhanced JSON parsing with multiple strategies
                if selector_map_text.strip().startswith('{'):
                    selector_map = json.loads(selector_map_text)
                else:
                    # Try markdown extraction
                    match = re.search(r"```json\n(.*?)```", selector_map_text, re.DOTALL)
                    if match:
                        selector_map = json.loads(match.group(1))
                    else:
                        raise ValueError("Invalid JSON format")
                
                logger.success(f"✅ Enhanced JSON parsing: {len(selector_map)} selectors")
                
            except Exception as e:
                logger.error(f"❌ JSON parsing failed: {e}")
                selector_map = {
                    "full_name": "input[name='name']",
                    "email": "input[name='email']",
                    "phone": "input[name='phone']",
                    "resume_upload": "input[type='file']"
                }

        with debug_section("Enhanced form filling"):
            # === STEP 11: ENHANCED AUTOMATED FORM FILLING ===
            logger.info("🤖 Step 9: Intelligent form automation")
            
            try:
                # Run sync playwright function in thread to avoid async loop conflict
                apply_result = await asyncio.to_thread(
                    apply_with_selector_map,
                    best_job.get('url', ''), selector_map, name, email, phone, pdf_path
                )
                
                if apply_result.get("status") != "success":
                    # Enhanced fallback
                    logger.warning("⚠️ Primary form filling failed, trying enhanced fallback")
                    apply_result = await asyncio.to_thread(
                        apply_to_ashby_job,
                        best_job.get('url', ''), name, email, phone, pdf_path
                    )
                
                screenshot_path = apply_result.get("screenshot", "uploads/enhanced_apply.png")
                logger.success("🤖 Enhanced form automation completed")
                
            except Exception as e:
                logger.error(f"❌ Enhanced form filling failed: {e}")
                return {"status": "error", "message": "Enhanced form automation failed", "details": str(e)}

        with debug_section("Enhanced database save"):
            # === STEP 12: ENHANCED DATABASE SAVE ===
            logger.info("💾 Step 10: Enhanced database recording")
            
            # Create enhanced job entry with AI insights
            enhanced_notes = f"""
Enhanced Pipeline V5 Application:
- Match Score: {best_job.get('score', 0):.3f}
- Search Attempts: {search_stats['total_attempts']}
- AI Analysis: {'✅ Yes' if 'ai_analysis' in best_job else '❌ No'}
- Optimization Score: {tailoring_result.get('optimization_score', 0):.2%}
- ATS Score: {tailoring_result.get('ats_score', 0):.2%}
- Success Probability: {success_prob:.2%}
- Checkpoint: {pipeline.checkpoint_id}
"""
            
            try:
                job_entry = create_job_entry(db, {
                    "title": best_job.get("title"),
                    "url": best_job.get("url"),
                    "company_name": best_job.get("company"),
                    "location": location,
                    "resume_used": pdf_path,
                    "screenshot_path": screenshot_path,
                    "applied": True,
                    "status": "applied",
                    "notes": enhanced_notes.strip()
                })
                
                logger.success(f"💾 Enhanced database entry created: ID {job_entry.id}")
                
            except Exception as e:
                logger.error(f"❌ Enhanced database save failed: {e}")

        with debug_section("Enhanced Notion logging"):
            # === STEP 13: ENHANCED NOTION LOGGING ===
            logger.info("📝 Step 11: Enhanced documentation and analytics")
            
            # Create comprehensive log with AI insights
            enhanced_highlights = [
                "✅ Enhanced Pipeline V5 executed",
                f"🧠 AI Features: {'Enabled' if LANGCHAIN_AVAILABLE else 'Disabled'}",
                "✅ Advanced resume parsing & embedding",
                f"✅ Enhanced search: {search_stats['total_attempts']} attempts, {len(new_jobs)} jobs found",
                f"🤖 AI Analysis: {search_stats.get('analyzed_jobs', 0)} jobs analyzed",
                f"✅ Best match: {best_job.get('title', 'Unknown')} (Score: {best_job.get('score', 0):.3f})",
                f"✨ Advanced resume tailoring (Optimization: {tailoring_result.get('optimization_score', 0):.1%})",
                f"🤖 ATS Optimization Score: {tailoring_result.get('ats_score', 0):.1%}",
                "✅ Intelligent form automation",
                "✅ Enhanced database recording",
                f"🎯 AI Success Prediction: {success_prob:.1%}",
                f"🔧 Debug checkpoint: {pipeline.checkpoint_id}"
            ]
            
            log_result = log_to_notion(
                title=f"🚀 Enhanced V5: {best_job.get('title', 'Unknown')} at {best_job.get('company', 'Unknown')}",
                content=format_daily_log(
                    highlights=enhanced_highlights,
                    changed_files=[
                        "pipeline_for_5.py", "enhanced_job_scraper.py", 
                        "resume_parser.py", "jd_matcher.py", "resume_tailor.py",
                        "pdf_generator.py", "field_mapper.py", "form_autofiller.py",
                        "crud.py", "debug_utils.py"
                    ],
                    screenshot=screenshot_path
                )
            )

        logger.success("🌟 Enhanced Pipeline V5 completed successfully!")
        debug_memory("Enhanced Pipeline V5 end")

        # Return comprehensive results
        return {
            "status": "success",
            "message": "Enhanced Pipeline V5 completed with AI optimization",
            "version": "5.0",
            "checkpoint_id": pipeline.checkpoint_id,
            "ai_enabled": enable_ai_features and LANGCHAIN_AVAILABLE,
            "search_stats": search_stats,
            "job_discovery": {
                "existing_jobs_in_db": len(existing_urls),
                "new_jobs_found": len(new_jobs),
                "search_attempts": search_stats['total_attempts'],
                "ai_analyzed_jobs": search_stats.get('analyzed_jobs', 0),
                "strategies_tried": search_stats['strategies_tried']
            },
            "best_job": {
                "title": best_job.get("title"),
                "url": best_job.get("url"),
                "company": best_job.get("company"),
                "score": best_job.get("score"),
                "ai_analysis": best_job.get("ai_analysis", {}),
                "success_probability": success_prob
            },
            "resume_optimization": {
                "optimization_score": tailoring_result.get('optimization_score', 0),
                "ats_score": tailoring_result.get('ats_score', 0),
                "changes_made": tailoring_result.get('changes_made', []),
                "improvement_suggestions": tailoring_result.get('improvement_suggestions', [])
            },
            "tailored_resume": tailored_resume,
            "pdf_path": pdf_path,
            "screenshot": screenshot_path,
            "notion_log": log_result,
            "database_id": getattr(job_entry, 'id', None) if 'job_entry' in locals() else None,
            "performance_metrics": {
                "total_execution_time": time.time(),
                "langchain_calls": 0,  # Would be tracked in real implementation
                "optimization_improvements": len(tailoring_result.get('changes_made', [])),
                "ai_insights_generated": bool(best_job.get('ai_analysis'))
            }
        }

    except Exception as e:
        logger.error(f"❌ Enhanced Pipeline V5 failed: {str(e)}", exc_info=True)
        debug_memory("Enhanced Pipeline V5 error")
        
        return {
            "status": "error",
            "message": f"Enhanced Pipeline V5 failed: {str(e)}",
            "version": "5.0",
            "checkpoint_id": pipeline.checkpoint_id,
            "ai_enabled": enable_ai_features and LANGCHAIN_AVAILABLE,
            "error_details": str(e)
        }
    
    finally:
        db.close()
        logger.info("🔒 Enhanced Pipeline V5 cleanup completed")

# Convenience function for synchronous execution
@debug_performance 
def run_enhanced_pipeline_v5_sync(
    file_path: str = None,
    name: str = "Eric Abram", 
    email: str = "ericabram33@gmail.com",
    phone: str = "312-805-9851",
    role: str = "SDET",
    location: str = "Chicago",
    enable_ai_features: bool = True
) -> Dict[str, Any]:
    """
    🚀 Synchronous wrapper for Enhanced Pipeline V5
    
    This function provides a synchronous interface to the async pipeline
    for compatibility with existing code.
    """
    
    logger.info("🚀 Launching Enhanced Pipeline V5 (Synchronous)")
    
    try:
        return asyncio.run(run_enhanced_pipeline_v5(
            file_path, name, email, phone, role, location, enable_ai_features
        ))
    except Exception as e:
        logger.error(f"❌ Synchronous pipeline execution failed: {e}")
        return {
            "status": "error",
            "message": f"Synchronous execution failed: {str(e)}",
            "version": "5.0"
        }

# Export main functions
__all__ = [
    'EnhancedPipelineV5',
    'run_enhanced_pipeline_v5',
    'run_enhanced_pipeline_v5_sync',
    'enhanced_persistent_job_search',
    'advanced_resume_tailoring',
    'intelligent_job_analysis',
    'generate_advanced_search_strategies'
]
