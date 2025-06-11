"""
🔧 COMPREHENSIVE DEBUGGING UTILITIES FOR AI JOB APPLICATION SYSTEM

This module provides advanced debugging tools to improve development workflow:
- Performance monitoring with execution time tracking
- Memory usage monitoring
- Function call logging with parameters and return values
- Error tracking with stack traces
- Database query debugging
- API request/response logging
- Custom debug decorators
- Development vs production debug levels

Usage Examples:
    @debug_performance
    def slow_function():
        time.sleep(1)
        return "result"
        
    @debug_api_call
    def api_request(url, data):
        return requests.post(url, json=data)
        
    debug_memory("Before processing")
    # ... some processing ...
    debug_memory("After processing")
"""

import time
import functools
import traceback
import psutil
import os
import json
import inspect
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from loguru import logger
import threading
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()   

# Debug configuration
DEBUG_ENABLED = os.getenv("DEBUG_MODE", "true").lower() == "true"
PERFORMANCE_LOGGING = os.getenv("PERF_LOGGING", "true").lower() == "true"
MEMORY_LOGGING = os.getenv("MEMORY_LOGGING", "true").lower() == "true"
API_LOGGING = os.getenv("API_LOGGING", "true").lower() == "true"

# Thread-local storage for request tracking
_thread_local = threading.local()

def get_memory_usage() -> Dict[str, float]:
    """
    📊 GET CURRENT MEMORY USAGE STATISTICS
    
    Returns detailed memory information including process memory,
    system memory, and memory percentages.
    
    Returns:
        Dict[str, float]: Memory statistics in MB and percentages
    """
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        system_memory = psutil.virtual_memory()
        
        return {
            "process_memory_mb": memory_info.rss / 1024 / 1024,
            "process_memory_percent": process.memory_percent(),
            "system_memory_percent": system_memory.percent,
            "available_memory_mb": system_memory.available / 1024 / 1024,
            "total_memory_mb": system_memory.total / 1024 / 1024
        }
    except Exception as e:
        logger.error(f"Failed to get memory usage: {e}")
        return {"error": str(e)}

def debug_memory(checkpoint: str = "") -> None:
    """
    🧠 LOG MEMORY USAGE AT CHECKPOINT
    
    Logs current memory usage with optional checkpoint label.
    Useful for tracking memory consumption through different stages.
    
    Args:
        checkpoint (str): Optional label for the memory checkpoint
    """
    if not DEBUG_ENABLED or not MEMORY_LOGGING:
        return
        
    memory_stats = get_memory_usage()
    if "error" not in memory_stats:
        logger.debug(
            f"🧠 MEMORY {checkpoint}: "
            f"Process: {memory_stats['process_memory_mb']:.1f}MB "
            f"({memory_stats['process_memory_percent']:.1f}%), "
            f"System: {memory_stats['system_memory_percent']:.1f}%, "
            f"Available: {memory_stats['available_memory_mb']:.1f}MB"
        )

def debug_performance(func: Callable) -> Callable:
    """
    ⏱️ PERFORMANCE MONITORING DECORATOR
    
    Decorates functions to automatically log execution time,
    memory usage before/after, and function parameters.
    
    Usage:
        @debug_performance
        def my_function(param1, param2):
            return result
    """
    if not DEBUG_ENABLED or not PERFORMANCE_LOGGING:
        return func
        
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__name__}"
        start_time = time.time()
        
        # Get memory before execution
        memory_before = get_memory_usage()
        
        # Log function entry
        logger.debug(f"⚡ ENTERING {func_name}")
        logger.debug(f"   📥 Args: {args[:3]}{'...' if len(args) > 3 else ''}")
        logger.debug(f"   📥 Kwargs: {dict(list(kwargs.items())[:3])}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Get memory after execution
            memory_after = get_memory_usage()
            memory_diff = memory_after.get('process_memory_mb', 0) - memory_before.get('process_memory_mb', 0)
            
            # Log successful completion
            logger.debug(f"✅ COMPLETED {func_name}")
            logger.debug(f"   ⏱️ Time: {execution_time:.3f}s")
            logger.debug(f"   🧠 Memory: {memory_diff:+.2f}MB")
            logger.debug(f"   📤 Result type: {type(result).__name__}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ FAILED {func_name}")
            logger.error(f"   ⏱️ Time: {execution_time:.3f}s")
            logger.error(f"   💥 Error: {str(e)}")
            logger.error(f"   📚 Stack trace:\n{traceback.format_exc()}")
            raise
            
    return wrapper

def debug_api_call(func: Callable) -> Callable:
    """
    🌐 API CALL DEBUGGING DECORATOR
    
    Decorates functions that make API calls to log requests,
    responses, timing, and error handling.
    
    Usage:
        @debug_api_call
        def call_openai_api(prompt):
            return openai.complete(prompt)
    """
    if not DEBUG_ENABLED or not API_LOGGING:
        return func
        
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__name__}"
        start_time = time.time()
        
        logger.debug(f"🌐 API CALL: {func_name}")
        logger.debug(f"   📤 Request args: {str(args)[:200]}...")
        logger.debug(f"   📤 Request kwargs: {str(kwargs)[:200]}...")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.debug(f"✅ API SUCCESS: {func_name}")
            logger.debug(f"   ⏱️ Response time: {execution_time:.3f}s")
            logger.debug(f"   📥 Response type: {type(result).__name__}")
            logger.debug(f"   📥 Response preview: {str(result)[:200]}...")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ API FAILED: {func_name}")
            logger.error(f"   ⏱️ Time: {execution_time:.3f}s")
            logger.error(f"   💥 Error: {str(e)}")
            logger.error(f"   📚 Full traceback:\n{traceback.format_exc()}")
            raise
            
    return wrapper

def debug_database(func: Callable) -> Callable:
    """
    🗄️ DATABASE OPERATION DEBUGGING DECORATOR
    
    Decorates database functions to log queries, execution time,
    and result counts.
    
    Usage:
        @debug_database
        def get_all_jobs(db):
            return db.query(Job).all()
    """
    if not DEBUG_ENABLED:
        return func
        
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__name__}"
        start_time = time.time()
        
        logger.debug(f"🗄️ DB OPERATION: {func_name}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Try to get result count if it's a list/collection
            result_info = ""
            if hasattr(result, '__len__'):
                result_info = f" ({len(result)} items)"
            elif hasattr(result, 'count'):
                result_info = f" ({result.count()} items)"
                
            logger.debug(f"✅ DB SUCCESS: {func_name}")
            logger.debug(f"   ⏱️ Query time: {execution_time:.3f}s")
            logger.debug(f"   📊 Result: {type(result).__name__}{result_info}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ DB FAILED: {func_name}")
            logger.error(f"   ⏱️ Time: {execution_time:.3f}s")
            logger.error(f"   💥 Error: {str(e)}")
            logger.error(f"   📚 Traceback:\n{traceback.format_exc()}")
            raise
            
    return wrapper

@contextmanager
def debug_section(section_name: str):
    """
    📍 CONTEXT MANAGER FOR DEBUGGING CODE SECTIONS
    
    Usage:
        with debug_section("Processing jobs"):
            # ... code here ...
            pass
    """
    if not DEBUG_ENABLED:
        yield
        return
        
    start_time = time.time()
    logger.debug(f"🟢 STARTING: {section_name}")
    debug_memory(f"Before {section_name}")
    
    try:
        yield
        execution_time = time.time() - start_time
        logger.debug(f"✅ COMPLETED: {section_name} ({execution_time:.3f}s)")
        debug_memory(f"After {section_name}")
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ FAILED: {section_name} ({execution_time:.3f}s)")
        logger.error(f"   💥 Error: {str(e)}")
        debug_memory(f"Failed {section_name}")
        raise

def debug_log_object(obj: Any, name: str = "Object", max_depth: int = 2) -> None:
    """
    🔍 LOG DETAILED OBJECT INFORMATION
    
    Logs object type, attributes, and values up to specified depth.
    Useful for debugging complex data structures.
    
    Args:
        obj: Object to debug
        name: Name/label for the object
        max_depth: Maximum depth to traverse nested objects
    """
    if not DEBUG_ENABLED:
        return
        
    def _format_value(value, depth=0):
        if depth >= max_depth:
            return f"{type(value).__name__}(...)"
            
        if isinstance(value, (str, int, float, bool, type(None))):
            return repr(value)
        elif isinstance(value, (list, tuple)):
            if len(value) <= 3:
                return f"[{', '.join(_format_value(v, depth+1) for v in value)}]"
            else:
                return f"[{_format_value(value[0], depth+1)}, ... +{len(value)-1} more]"
        elif isinstance(value, dict):
            if len(value) <= 3:
                items = [f"{k}: {_format_value(v, depth+1)}" for k, v in list(value.items())[:3]]
                return f"{{{', '.join(items)}}}"
            else:
                return f"{{...{len(value)} keys...}}"
        else:
            return f"{type(value).__name__}(...)"
    
    logger.debug(f"🔍 DEBUG {name}:")
    logger.debug(f"   📝 Type: {type(obj).__name__}")
    
    if hasattr(obj, '__dict__'):
        for attr_name, attr_value in obj.__dict__.items():
            if not attr_name.startswith('_'):
                formatted_value = _format_value(attr_value)
                logger.debug(f"   📋 {attr_name}: {formatted_value}")
    elif isinstance(obj, dict):
        for key, value in list(obj.items())[:10]:  # Limit to first 10 items
            formatted_value = _format_value(value)
            logger.debug(f"   📋 {key}: {formatted_value}")
    else:
        formatted_value = _format_value(obj)
        logger.debug(f"   📋 Value: {formatted_value}")

def debug_function_calls(track_all: bool = False):
    """
    📞 ENABLE FUNCTION CALL TRACKING
    
    When enabled, logs all function calls with parameters.
    Use sparingly as it can generate a lot of output.
    
    Args:
        track_all: If True, tracks all function calls in the module
    """
    if not DEBUG_ENABLED or not track_all:
        return
        
    def trace_calls(frame, event, arg):
        if event == 'call':
            func_name = frame.f_code.co_name
            filename = frame.f_code.co_filename
            if 'ai_job_app' in filename:  # Only track our application calls
                logger.debug(f"📞 CALL: {func_name} in {os.path.basename(filename)}")
        return trace_calls
    
    import sys
    sys.settrace(trace_calls)

def create_debug_checkpoint() -> str:
    """
    🏁 CREATE DEBUG CHECKPOINT
    
    Creates a unique checkpoint ID with timestamp for tracking
    execution flow across multiple functions.
    
    Returns:
        str: Unique checkpoint ID
    """
    checkpoint_id = f"checkpoint_{datetime.now().strftime('%H%M%S%f')[:-3]}"
    logger.debug(f"🏁 CHECKPOINT CREATED: {checkpoint_id}")
    return checkpoint_id

def debug_environment() -> None:
    """
    🌍 LOG CURRENT ENVIRONMENT INFORMATION
    
    Logs system information, environment variables,
    and application configuration for debugging.
    """
    if not DEBUG_ENABLED:
        return
        
    logger.debug("🌍 ENVIRONMENT DEBUG INFO:")
    logger.debug(f"   🐍 Python: {os.sys.version}")
    logger.debug(f"   💻 OS: {os.name}")
    logger.debug(f"   📁 CWD: {os.getcwd()}")
    logger.debug(f"   🧠 Memory: {get_memory_usage()['process_memory_mb']:.1f}MB")
    
    # Log relevant environment variables
    env_vars = ['DEBUG_MODE', 'PERF_LOGGING', 'MEMORY_LOGGING', 'API_LOGGING', 
                'OPENAI_API_KEY', 'API_KEY', 'NOTION_API_KEY', 'CSE_ID', 'NOTION_DB_ID']
    for var in env_vars:
        value = os.getenv(var, 'NOT_SET')
        # Mask sensitive values
        if 'KEY' in var or 'TOKEN' in var:
            display_value = value[:8] + '...' if value != 'NOT_SET' else 'NOT_SET'
        else:
            display_value = value
        logger.debug(f"   🔧 {var}: {display_value}")

# Initialize debugging when module is imported
if DEBUG_ENABLED:
    logger.debug("🔧 Debug utilities initialized")
    debug_environment()

@debug_performance
def your_function():
    pass 