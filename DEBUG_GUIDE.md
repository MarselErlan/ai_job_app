# 🔧 AI Job Application System - Debugging Guide

This guide explains the comprehensive debugging features that have been added to your AI job application system to improve your development workflow and make troubleshooting much easier.

## 🎯 Quick Start

1. **Enable Debug Mode:**

   ```bash
   export DEBUG_MODE=true
   export PERF_LOGGING=true
   export MEMORY_LOGGING=true
   export API_LOGGING=true
   ```

2. **Test Debugging Features:**

   ```bash
   python debug_test.py
   ```

3. **Start Your Application:**

   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Check Debug Endpoints:**
   - Health Check: http://localhost:8000/health
   - Debug Stats: http://localhost:8000/debug/stats
   - API Docs: http://localhost:8000/docs

## 🛠️ Debugging Features Overview

### 1. Performance Monitoring (`@debug_performance`)

Automatically tracks execution time, memory usage, and function parameters.

```python
from app.utils.debug_utils import debug_performance

@debug_performance
def your_function(param1, param2):
    # Your code here
    return result
```

**What it logs:**

- Function entry with parameters
- Execution time
- Memory usage before/after
- Return value type
- Full stack traces on errors

### 2. API Call Debugging (`@debug_api_call`)

Monitors external API calls with request/response logging.

```python
from app.utils.debug_utils import debug_api_call

@debug_api_call
def call_openai_api(prompt):
    response = openai.complete(prompt)
    return response
```

**What it logs:**

- Request parameters (sanitized)
- Response time
- Response size and type
- API errors with details
- Rate limiting information

### 3. Database Debugging (`@debug_database`)

Tracks database operations with performance metrics.

```python
from app.utils.debug_utils import debug_database

@debug_database
def get_jobs_from_db(db):
    return db.query(Job).all()
```

**What it logs:**

- Query execution time
- Number of records affected
- Database connection health
- Slow query warnings
- Transaction details

### 4. Memory Monitoring

Track memory usage at any point in your code.

```python
from app.utils.debug_utils import debug_memory

debug_memory("Before processing")
# Your code here
debug_memory("After processing")
```

**What it logs:**

- Process memory usage in MB
- System memory percentage
- Available memory
- Memory differences between checkpoints

### 5. Code Section Debugging

Time and monitor specific code blocks.

```python
from app.utils.debug_utils import debug_section

with debug_section("Processing jobs"):
    # Your code block here
    process_jobs()
```

**What it logs:**

- Section start/end times
- Memory usage before/after
- Any errors within the section
- Nested section support

### 6. Object Inspection

Debug complex data structures and objects.

```python
from app.utils.debug_utils import debug_log_object

job_data = {"title": "SDET", "company": "TechCorp", ...}
debug_log_object(job_data, "Job application data")
```

**What it logs:**

- Object type and structure
- Nested object exploration
- Large collection summaries
- Circular reference protection

### 7. Execution Checkpoints

Create unique identifiers to track execution flow.

```python
from app.utils.debug_utils import create_debug_checkpoint

checkpoint_id = create_debug_checkpoint()
logger.info(f"Processing job with checkpoint: {checkpoint_id}")
```

**What it provides:**

- Unique timestamp-based IDs
- Easy correlation across logs
- Pipeline stage tracking

## 📊 Enhanced Components

### Database Operations (app/db/crud.py)

**New Features:**

- Query performance monitoring
- Connection health checks
- Slow query detection
- Database statistics collection
- Transaction debugging

**Usage:**

```python
from app.db.crud import get_database_statistics, log_database_health

# Get performance stats
stats = get_database_statistics()
print(f"Average query time: {stats['average_query_time']:.3f}s")

# Log health summary
log_database_health()
```

### Job Scraper (app/services/job_scraper.py)

**New Features:**

- API configuration validation
- Request/response logging
- Company name extraction
- Search statistics
- Error recovery

**What it logs:**

- API key configuration status
- Search query details
- Response parsing results
- Duplicate detection
- Performance metrics

### Main Pipeline (app/tasks/pipeline.py)

**New Features:**

- Execution checkpoints
- Memory tracking per stage
- Section-based timing
- Detailed error context
- Statistics collection

**Enhanced sections:**

- Resume processing
- Job search with statistics
- Database operations
- Form filling
- Notion logging

### FastAPI Application (app/main.py)

**New Features:**

- Request/response middleware
- Health check endpoint
- Debug endpoints (development only)
- Performance statistics
- Error tracking

**Debug Endpoints:**

- `GET /health` - System health check
- `GET /debug/stats` - API statistics
- `GET /debug/memory` - Memory usage
- `GET /debug/database` - Database health
- `POST /debug/checkpoint` - Create checkpoint

### API Endpoints (app/api/v1/resume.py)

**New Features:**

- Input validation debugging
- File upload monitoring
- Processing time tracking
- Error context
- Endpoint statistics

## ⚙️ Configuration

### Environment Variables

```bash
# Core debugging
DEBUG_MODE=true              # Enable all debugging features
PERF_LOGGING=true           # Performance monitoring
MEMORY_LOGGING=true         # Memory usage tracking
API_LOGGING=true            # API call debugging

# Performance thresholds
SLOW_QUERY_THRESHOLD=1.0    # Database query warning (seconds)
SLOW_API_THRESHOLD=5.0      # API call warning (seconds)
MEMORY_WARNING_THRESHOLD=500 # Memory usage warning (MB)

# Development features
ENABLE_STACK_TRACES=true    # Detailed error traces
SAVE_INTERMEDIATE_FILES=true # Keep debug files
```

### Debug Configuration File

Copy `debug_config.env` to `.env` and customize:

```bash
cp debug_config.env .env
# Edit .env with your preferred settings
```

## 📈 Monitoring & Statistics

### Database Statistics

```python
from app.db.crud import get_database_statistics

stats = get_database_statistics()
# Returns: query counts, timing, performance metrics
```

### API Statistics

Access via debug endpoints or programmatically:

```bash
curl http://localhost:8000/debug/stats
```

### Memory Usage

Real-time memory monitoring:

```bash
curl http://localhost:8000/debug/memory
```

## 🚨 Troubleshooting

### Common Issues

1. **High Memory Usage:**

   ```python
   # Add memory checkpoints to identify leaks
   debug_memory("Before operation")
   your_operation()
   debug_memory("After operation")
   ```

2. **Slow Database Queries:**

   ```python
   # Database operations are automatically monitored
   # Check logs for slow query warnings
   # Use get_database_statistics() for details
   ```

3. **API Call Failures:**

   ```python
   # API calls are automatically logged with @debug_api_call
   # Check logs for request/response details
   # Verify API configuration with validate_api_configuration()
   ```

4. **Pipeline Stage Failures:**
   ```python
   # Each pipeline stage has its own debug section
   # Use checkpoint IDs to track execution flow
   # Check memory usage between stages
   ```

### Debug Logs Location

Logs are output via loguru with different levels:

- `DEBUG`: Detailed debugging information
- `INFO`: General information
- `WARNING`: Performance warnings
- `ERROR`: Error details with stack traces
- `SUCCESS`: Successful operations

### Performance Optimization

1. **Identify Bottlenecks:**

   - Use `@debug_performance` on suspicious functions
   - Monitor database query times
   - Check memory usage patterns

2. **API Optimization:**

   - Monitor API response times
   - Check for rate limiting
   - Validate request/response sizes

3. **Memory Management:**
   - Use `debug_memory()` at key points
   - Monitor memory growth patterns
   - Identify memory leaks

## 🧪 Testing Your Debugging Setup

Run the comprehensive test suite:

```bash
python debug_test.py
```

This will test:

- ✅ Basic debugging utilities
- ✅ Performance monitoring
- ✅ API call debugging
- ✅ Database operations
- ✅ Memory monitoring
- ✅ Error handling
- ✅ Async function debugging

## 💡 Best Practices

### 1. Use Appropriate Debug Levels

```python
# For functions that might be slow
@debug_performance
def process_large_dataset():
    pass

# For external API calls
@debug_api_call
def call_external_service():
    pass

# For database operations
@debug_database
def query_database():
    pass
```

### 2. Strategic Memory Monitoring

```python
# Monitor memory at key pipeline stages
debug_memory("Start pipeline")
parse_resume()
debug_memory("After resume parsing")
search_jobs()
debug_memory("After job search")
apply_to_jobs()
debug_memory("End pipeline")
```

### 3. Use Checkpoints for Flow Tracking

```python
checkpoint = create_debug_checkpoint()
logger.info(f"Starting job application with checkpoint: {checkpoint}")
# Include checkpoint in database records for traceability
```

### 4. Debug Sections for Complex Operations

```python
with debug_section("Complete job application"):
    with debug_section("Resume tailoring"):
        tailor_resume()

    with debug_section("PDF generation"):
        generate_pdf()

    with debug_section("Form submission"):
        submit_application()
```

## 🔍 Production Considerations

### Disabling Debug Features

For production, set:

```bash
DEBUG_MODE=false
PERF_LOGGING=false
MEMORY_LOGGING=false
API_LOGGING=false
```

### Keeping Essential Monitoring

Even in production, consider keeping:

- Health check endpoint
- Basic error logging
- Performance statistics (without detailed logs)
- Database health monitoring

### Security

- Debug endpoints are automatically disabled when `DEBUG_MODE=false`
- Sensitive data in logs is automatically sanitized
- Stack traces can be disabled with `ENABLE_STACK_TRACES=false`

## 📚 Additional Resources

- **Health Check:** `GET /health` - System status
- **API Documentation:** `/docs` (development only)
- **Debug Test Script:** `python debug_test.py`
- **Configuration Template:** `debug_config.env`

## 🎉 Summary

Your AI job application system now includes:

✅ **Comprehensive performance monitoring**  
✅ **Memory usage tracking**  
✅ **Database operation debugging**  
✅ **API call monitoring**  
✅ **Error tracking with detailed context**  
✅ **Health monitoring endpoints**  
✅ **Development vs production configurations**  
✅ **Automated testing and reporting**

This debugging infrastructure will help you:

- **Identify bottlenecks quickly**
- **Track down errors with detailed context**
- **Monitor system health in real-time**
- **Optimize performance based on data**
- **Debug complex pipeline flows**
- **Maintain code quality over time**

Happy debugging! 🚀
