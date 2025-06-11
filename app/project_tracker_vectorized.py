# 📁 project_tracker_vectorized.py
"""
🤖 ENHANCED AI PROJECT TRACKER WITH VECTORIZED ANALYSIS

This tool provides comprehensive project analysis similar to about_project.txt
but generates it automatically using LangChain and vector embeddings for speed.
It maintains the fast vectorized approach while providing detailed insights.
"""

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import pandas as pd
import numpy as np

# === CONFIG ===
SOURCE_DIR = "./app"
VECTOR_DB_DIR = "./vector_db"
OUTPUT_DIR = "./outputs"
OUTPUT_FILE = f"{OUTPUT_DIR}/about_project_auto_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

print("🚀 Starting Enhanced AI Project Tracker with Pandas Analytics...")
print(f"📁 Analyzing: {SOURCE_DIR}")
print(f"💾 Output: {OUTPUT_FILE}")

# === STEP 1: Advanced File Loading with Metadata ===
def load_project_files():
    """Load all Python files with enhanced metadata"""
    loader = DirectoryLoader(
        path=SOURCE_DIR,
        glob="**/*.py",
        recursive=True,
        show_progress=True
    )
    documents = loader.load()
    
    # Enhance metadata with file analysis
    for doc in documents:
        file_path = doc.metadata.get("source", "")
        relative_path = file_path.replace(SOURCE_DIR + "/", "") if SOURCE_DIR in file_path else file_path
        
        # Count lines and functions
        content = doc.page_content
        lines = content.splitlines()
        functions = len(re.findall(r'^def\s+\w+\(', content, re.MULTILINE))
        classes = len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
        
        doc.metadata.update({
            "relative_path": relative_path,
            "line_count": len(lines),
            "function_count": functions,
            "class_count": classes,
            "file_size_kb": round(len(content.encode('utf-8')) / 1024, 1)
        })
    
    return documents

documents = load_project_files()
print(f"📊 Loaded {len(documents)} Python files")

# === STEP 2: Advanced File Analysis ===
def analyze_file_importance(docs):
    """Analyze and categorize files by importance and functionality"""
    
    # File importance scoring based on size, complexity, and role
    importance_scores = {}
    file_categories = {}
    
    # Define file categories and their importance weights
    category_patterns = {
        "Core Pipeline": {
            "patterns": ["pipeline", "tasks"],
            "weight": 0.35,
            "description": "Main orchestrators that coordinate the entire process"
        },
        "Service Layer": {
            "patterns": ["services", "resume_parser", "job_scraper", "form_autofiller", "field_mapper", "notion_logger", "pdf_generator", "resume_tailor", "jd_matcher"],
            "weight": 0.25,
            "description": "Specialized modules handling specific tasks"
        },
        "API & Web Layer": {
            "patterns": ["main.py", "api", "endpoints"],
            "weight": 0.15,
            "description": "Web interface and HTTP endpoints"
        },
        "Database Layer": {
            "patterns": ["db", "crud", "models", "session"],
            "weight": 0.12,
            "description": "Data persistence and management"
        },
        "Infrastructure": {
            "patterns": ["utils", "debug", "core", "config"],
            "weight": 0.08,
            "description": "Supporting utilities and debugging"
        },
        "Configuration": {
            "patterns": ["schemas", "__init__"],
            "weight": 0.05,
            "description": "Configuration and setup files"
        }
    }
    
    total_lines = sum(doc.metadata["line_count"] for doc in docs)
    
    for doc in docs:
        file_path = doc.metadata["relative_path"].lower()
        line_count = doc.metadata["line_count"]
        
        # Categorize file
        category = "Other"
        for cat_name, cat_info in category_patterns.items():
            if any(pattern in file_path for pattern in cat_info["patterns"]):
                category = cat_name
                break
        
        file_categories[doc.metadata["relative_path"]] = category
        
        # Calculate importance score
        size_score = (line_count / total_lines) * 100
        complexity_score = (doc.metadata["function_count"] + doc.metadata["class_count"]) * 0.1
        category_weight = category_patterns.get(category, {"weight": 0.02})["weight"]
        
        importance_scores[doc.metadata["relative_path"]] = round(size_score * category_weight * 100, 1)
    
    return importance_scores, file_categories, category_patterns

importance_scores, file_categories, category_info = analyze_file_importance(documents)

# === STEP 3: Generate Detailed File Breakdown ===
def generate_file_breakdown(docs, scores, categories):
    """Generate detailed file-by-file breakdown"""
    
    breakdown = {}
    for category in category_info.keys():
        breakdown[category] = []
    breakdown["Other"] = []  # Add "Other" category
    
    for doc in docs:
        rel_path = doc.metadata["relative_path"]
        category = categories.get(rel_path, "Other")
        
        file_info = {
            "path": rel_path,
            "lines": doc.metadata["line_count"],
            "functions": doc.metadata["function_count"],
            "classes": doc.metadata["class_count"],
            "size_kb": doc.metadata["file_size_kb"],
            "importance": scores.get(rel_path, 0),
            "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
        }
        
        breakdown[category].append(file_info)
    
    # Sort by importance within each category
    for category in breakdown:
        breakdown[category].sort(key=lambda x: x["importance"], reverse=True)
    
    return breakdown

file_breakdown = generate_file_breakdown(documents, importance_scores, file_categories)

# === STEP 4: Enhanced Completion Analysis ===
def advanced_completion_analysis(docs):
    """Advanced analysis of project completion and quality"""
    
    total_lines = 0
    incomplete_indicators = {
        "TODO": 0,
        "FIXME": 0,
        "pass": 0,
        "raise NotImplementedError": 0,
        "# TODO": 0,
        "# FIXME": 0,
        "...": 0
    }
    
    quality_indicators = {
        "docstrings": 0,
        "comments": 0,
        "type_hints": 0,
        "error_handling": 0,
        "logging": 0
    }
    
    for doc in docs:
        content = doc.page_content
        lines = content.splitlines()
        total_lines += len(lines)
        
        # Count incomplete indicators
        for indicator in incomplete_indicators:
            incomplete_indicators[indicator] += content.count(indicator)
        
        # Count quality indicators
        quality_indicators["docstrings"] += content.count('"""')
        quality_indicators["comments"] += len([l for l in lines if l.strip().startswith("#")])
        quality_indicators["type_hints"] += content.count(" -> ")
        quality_indicators["error_handling"] += content.count("try:") + content.count("except")
        quality_indicators["logging"] += content.count("logger.")
    
    # Calculate completion percentage
    total_incomplete = sum(incomplete_indicators.values())
    completion_percent = max(0, round(((total_lines - total_incomplete) / total_lines) * 100, 1)) if total_lines > 0 else 100
    
    return {
        "completion_percent": completion_percent,
        "total_lines": total_lines,
        "incomplete_indicators": incomplete_indicators,
        "quality_indicators": quality_indicators
    }

completion_analysis = advanced_completion_analysis(documents)

# === PANDAS STYLING FUNCTIONS ===
def create_file_summary_table(breakdown, total_lines):
    """Create a professional pandas table of file statistics"""
    
    data = []
    for category, files in breakdown.items():
        if not files:
            continue
            
        category_lines = sum(f["lines"] for f in files)
        category_functions = sum(f["functions"] for f in files)
        category_classes = sum(f["classes"] for f in files)
        category_size = sum(f["size_kb"] for f in files)
        percentage = round((category_lines / total_lines) * 100, 1) if total_lines > 0 else 0
        
        data.append({
            "Category": category,
            "Files": len(files),
            "Lines of Code": f"{category_lines:,}",
            "Functions": category_functions,
            "Classes": category_classes,
            "Size (KB)": f"{category_size:.1f}",
            "% of Codebase": f"{percentage}%"
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values("% of Codebase", key=lambda x: pd.to_numeric(x.str.rstrip('%')), ascending=False)
    return df

def create_top_files_table(breakdown, top_n=15):
    """Create a table of the most important files across all categories"""
    
    all_files = []
    for category, files in breakdown.items():
        for file_info in files:
            file_info_copy = file_info.copy()
            file_info_copy["category"] = category
            all_files.append(file_info_copy)
    
    # Sort by importance
    all_files.sort(key=lambda x: x["importance"], reverse=True)
    
    data = []
    for file_info in all_files[:top_n]:
        data.append({
            "File": file_info["path"].split('/')[-1],  # Just filename
            "Full Path": file_info["path"],
            "Category": file_info["category"],
            "Lines": f"{file_info['lines']:,}",
            "Functions": file_info["functions"],
            "Classes": file_info["classes"],
            "Size (KB)": f"{file_info['size_kb']:.1f}",
            "Importance": f"{file_info['importance']:.1f}%",
            "Critical": "⭐" if file_info["importance"] > 2 else ""
        })
    
    return pd.DataFrame(data)

def create_quality_metrics_table(completion_analysis):
    """Create a professional table of code quality metrics"""
    
    quality = completion_analysis["quality_indicators"]
    incomplete = completion_analysis["incomplete_indicators"]
    
    data = [
        ["Metric", "Value", "Status"],
        ["Overall Completion", f"{completion_analysis['completion_percent']}%", 
         "✅ Excellent" if completion_analysis['completion_percent'] > 90 else "🔄 Good" if completion_analysis['completion_percent'] > 70 else "⚠️ Needs Work"],
        ["Total Lines of Code", f"{completion_analysis['total_lines']:,}", "📊 Info"],
        ["Documentation (Docstrings)", f"{quality['docstrings']}", 
         "✅ High" if quality['docstrings'] > 50 else "📝 Medium" if quality['docstrings'] > 20 else "⚠️ Low"],
        ["Error Handling (Try/Except)", f"{quality['error_handling']}", 
         "🛡️ Robust" if quality['error_handling'] > 50 else "🔧 Moderate" if quality['error_handling'] > 20 else "⚠️ Basic"],
        ["Logging Coverage", f"{quality['logging']}", 
         "📊 Excellent" if quality['logging'] > 100 else "📈 Good" if quality['logging'] > 50 else "📝 Basic"],
        ["Comments", f"{quality['comments']:,}", "📝 Info"],
        ["Type Hints", f"{quality['type_hints']}", "🔍 Info"],
        ["TODO/FIXME Items", f"{sum(incomplete.values())}", 
         "✅ Clean" if sum(incomplete.values()) < 10 else "🔄 Some" if sum(incomplete.values()) < 50 else "⚠️ Many"]
    ]
    
    df = pd.DataFrame(data[1:], columns=data[0])  # Use first row as header
    return df

def format_pandas_table_for_text(df, title="", max_width=120):
    """Convert pandas DataFrame to nicely formatted text table"""
    
    result = []
    if title:
        result.append(f"\n{'=' * len(title)}")
        result.append(f"{title}")
        result.append(f"{'=' * len(title)}")
    
    # Configure pandas display options for cleaner output
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', max_width)
    pd.set_option('display.max_colwidth', 30)
    
    table_str = df.to_string(index=False, justify='left')
    result.append(table_str)
    result.append("")
    
    return "\n".join(result)

def generate_file_detail_tables(breakdown):
    """Generate detailed tables for each category"""
    
    tables = []
    
    for category, files in breakdown.items():
        if not files or len(files) == 0:
            continue
            
        # Create DataFrame for this category
        data = []
        for file_info in files[:10]:  # Top 10 files per category
            data.append({
                "File": file_info["path"].split('/')[-1],
                "Lines": f"{file_info['lines']:,}",
                "Functions": file_info["functions"],
                "Classes": file_info["classes"],
                "Size (KB)": f"{file_info['size_kb']:.1f}",
                "Importance": f"{file_info['importance']:.1f}%"
            })
        
        if data:
            df = pd.DataFrame(data)
            table_text = format_pandas_table_for_text(
                df, 
                title=f"{category} - Top Files"
            )
            tables.append(table_text)
    
    return "\n".join(tables)

# === STEP 5: Enhanced Vector Embeddings ===
print("🧠 Creating enhanced vector embeddings...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500, 
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)
chunks = splitter.split_documents(documents)

embedding = OpenAIEmbeddings()
vectordb = Chroma.from_documents(chunks, embedding, persist_directory=VECTOR_DB_DIR)
vectordb.persist()

# === STEP 6: Enhanced Analysis Prompts ===
ENHANCED_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["context"],
    template="""
You are an expert software architect analyzing an AI job application system.

Based on the code chunks provided, generate a comprehensive technical analysis.

CODE CONTEXT:
{context}

Provide detailed, technical insights that would help a developer understand this system after months away from the code. Focus on:
- What the code does and why it's important
- How components interact with each other  
- Key technical decisions and architecture patterns
- Performance considerations and optimization opportunities
- Error handling and reliability mechanisms

Be specific and technical, but also clear for future reference.
"""
)

# === STEP 7: Multi-Perspective Analysis ===
def run_enhanced_analysis():
    """Run multiple focused analyses using the vector database"""
    
    retriever = vectordb.as_retriever(search_kwargs={"k": 15})
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": ENHANCED_ANALYSIS_PROMPT}
    )
    
    analyses = {}
    
    analysis_focuses = [
        "system architecture and overall design patterns",
        "core pipeline functionality and data flow",
        "AI and machine learning integration (OpenAI, embeddings, GPT)",
        "external API integrations and service dependencies", 
        "database design and data persistence strategies",
        "error handling, debugging, and reliability mechanisms",
        "performance optimization and scalability considerations"
    ]
    
    print("🔍 Running multi-perspective analysis...")
    for focus in analysis_focuses:
        print(f"  📊 Analyzing: {focus}")
        try:
            query = f"Analyze the {focus} in this codebase with specific examples and technical details"
            analyses[focus] = qa_chain.invoke({"query": query})["result"]
        except Exception as e:
            print(f"  ⚠️ Analysis failed for {focus}: {e}")
            analyses[focus] = f"Analysis unavailable due to: {e}"
    
    return analyses

enhanced_analyses = run_enhanced_analysis()

# === STEP 8: Generate Comprehensive Report ===
def generate_comprehensive_report():
    """Generate the final comprehensive report with pandas tables"""
    
    report = []
    
    # Header
    report.append("🤖 AI JOB APPLICATION SYSTEM - AUTOMATED COMPREHENSIVE ANALYSIS")
    report.append("═" * 80)
    report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"📁 Source: {SOURCE_DIR}")
    report.append(f"📊 Files Analyzed: {len(documents)}")
    report.append("")
    
    # Executive Summary
    report.append("## 🎯 EXECUTIVE SUMMARY")
    report.append("")
    report.append("This is an intelligent, fully automated job application system that acts as your")
    report.append("personal AI job hunter. It automates the entire process from resume parsing to")
    report.append("job application submission using AI, browser automation, and smart algorithms.")
    report.append("")
    
    # === PANDAS ENHANCED SECTIONS ===
    
    # 1. Project Status with Quality Metrics Table
    report.append("## 📈 PROJECT STATUS & QUALITY METRICS")
    report.append("")
    quality_table = create_quality_metrics_table(completion_analysis)
    report.append(format_pandas_table_for_text(quality_table, "Code Quality Analysis"))
    
    # 2. File Distribution Summary Table
    total_lines = sum(doc.metadata["line_count"] for doc in documents)
    summary_table = create_file_summary_table(file_breakdown, total_lines)
    report.append("## 📊 CODEBASE DISTRIBUTION SUMMARY")
    report.append("")
    report.append(format_pandas_table_for_text(summary_table, "File Categories Overview"))
    
    # 3. Top Critical Files Table
    report.append("## ⭐ MOST CRITICAL FILES (Top 15)")
    report.append("")
    top_files_table = create_top_files_table(file_breakdown, top_n=15)
    report.append(format_pandas_table_for_text(top_files_table, "Critical Components Ranked by Importance"))
    
    # 4. Detailed Category Breakdown
    report.append("## 📁 DETAILED FILE BREAKDOWN BY CATEGORY")
    report.append("")
    report.append(generate_file_detail_tables(file_breakdown))
    
    # Technical Analysis Sections (Enhanced with better formatting)
    report.append("## 🔧 AI-POWERED TECHNICAL ANALYSIS")
    report.append("")
    report.append("The following sections were generated using AI analysis of the codebase:")
    report.append("")
    
    for focus, analysis in enhanced_analyses.items():
        section_title = focus.replace("and", "&").title()
        report.append(f"### 🔍 {section_title}")
        report.append("")
        
        # Clean up the analysis text
        clean_analysis = analysis.strip()
        if len(clean_analysis) > 50:  # Only include substantial analysis
            # Add some formatting to make it more readable
            paragraphs = clean_analysis.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    report.append(paragraph.strip())
                    report.append("")
        else:
            report.append("Analysis is being processed or unavailable.")
            report.append("")
    
    # Key Insights with enhanced formatting
    report.append("## 💡 KEY INSIGHTS & RECOMMENDATIONS")
    report.append("")
    
    # Auto-generate insights based on analysis
    insights = []
    
    completion_pct = completion_analysis['completion_percent']
    error_handling = completion_analysis['quality_indicators']['error_handling']
    logging_count = completion_analysis['quality_indicators']['logging']
    
    if completion_pct > 90:
        insights.append("✅ **High Completion Rate** - System is production-ready with excellent code coverage")
    elif completion_pct > 70:
        insights.append("🔄 **Good Progress** - System is largely functional with room for enhancement")
    else:
        insights.append("⚠️ **Development Stage** - Core functionality present but needs completion")
    
    if error_handling > 50:
        insights.append("🛡️ **Robust Error Handling** - System has comprehensive error recovery mechanisms")
    elif error_handling > 20:
        insights.append("🔧 **Moderate Error Handling** - Basic error recovery in place, could be enhanced")
    else:
        insights.append("⚠️ **Limited Error Handling** - Consider adding more try/except blocks")
    
    if logging_count > 100:
        insights.append("📊 **Excellent Observability** - Comprehensive logging for debugging and monitoring")
    elif logging_count > 50:
        insights.append("📈 **Good Logging Coverage** - Adequate logging for most operations")
    else:
        insights.append("📝 **Basic Logging** - Consider adding more logging for better observability")
    
    # Find most important files
    all_files = []
    for files in file_breakdown.values():
        all_files.extend(files)
    
    top_files = sorted(all_files, key=lambda x: x["importance"], reverse=True)[:5]
    insights.append(f"🎯 **Core Components**: {', '.join([f['path'].split('/')[-1] for f in top_files])}")
    
    # Add architecture insights
    core_pipeline_files = len([f for f in all_files if "pipeline" in f["path"].lower()])
    service_files = len([f for f in all_files if "services" in f["path"].lower()])
    
    if core_pipeline_files > 1:
        insights.append("🏗️ **Modular Architecture** - Well-structured pipeline design with clear separation")
    
    if service_files > 5:
        insights.append("🔧 **Service-Oriented Design** - Good separation of concerns with dedicated service modules")
    
    for insight in insights:
        report.append(insight)
        report.append("")
    
    # Usage Instructions with better formatting
    report.append("## 🚀 SYSTEM USAGE")
    report.append("")
    report.append("```bash")
    report.append("# Start the system")
    report.append("uvicorn app.main:app --reload")
    report.append("")
    report.append("# Access interactive API documentation")
    report.append("open http://localhost:8000/docs")
    report.append("")
    report.append("# Run complete pipeline via API")
    report.append("curl -X POST 'http://localhost:8000/api/v1/pipeline/apply-multi' \\")
    report.append("  -H 'Content-Type: application/json' \\")
    report.append("  -d '{")
    report.append('    "resume_filename": "resume.pdf",')
    report.append('    "name": "Your Name",')
    report.append('    "email": "email@domain.com",')
    report.append('    "phone": "555-1234",')
    report.append('    "role": "SDET",')
    report.append('    "location": "Chicago"')
    report.append("  }'")
    report.append("")
    report.append("# Generate updated project analysis")
    report.append("python app/project_tracker_vectorized.py")
    report.append("```")
    report.append("")
    
    # Statistics Summary
    report.append("## 📊 PROJECT STATISTICS SUMMARY")
    report.append("")
    critical_files = len([f for f in all_files if f["importance"] > 2])
    total_functions = sum(f["functions"] for f in all_files)
    total_classes = sum(f["classes"] for f in all_files)
    
    stats_data = [
        ["Statistic", "Value"],
        ["Total Files Analyzed", f"{len(documents)}"],
        ["Total Lines of Code", f"{completion_analysis['total_lines']:,}"],
        ["Critical Components", f"{critical_files}"],
        ["Total Functions", f"{total_functions:,}"],
        ["Total Classes", f"{total_classes}"],
        ["Documentation Quality", f"{'High' if completion_analysis['quality_indicators']['docstrings'] > 50 else 'Medium'}"],
        ["Project Completion", f"{completion_analysis['completion_percent']}%"]
    ]
    
    stats_df = pd.DataFrame(stats_data[1:], columns=stats_data[0])
    report.append(format_pandas_table_for_text(stats_df, "Key Project Metrics"))
    
    # Footer
    report.append("---")
    report.append(f"📋 Report generated automatically by Enhanced AI Project Tracker with Pandas Analytics")
    report.append(f"🕒 Analysis completed in vectorized processing mode for optimal speed")
    report.append(f"📊 Professional data formatting powered by pandas and numpy")
    report.append(f"🔄 Re-run this script anytime to get updated project analysis with clean tables")
    
    return "\n".join(report)

# === STEP 9: Generate and Save Report ===
print("📝 Generating comprehensive report...")
comprehensive_report = generate_comprehensive_report()

# Save report
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(comprehensive_report)

print(f"✅ Comprehensive analysis saved to: {OUTPUT_FILE}")
print(f"📊 Analyzed {len(documents)} files with {completion_analysis['total_lines']:,} lines of code")
print(f"🎯 Project completion: {completion_analysis['completion_percent']}%")
print(f"⭐ Found {len([f for files in file_breakdown.values() for f in files if f['importance'] > 2])} critical components")

# === STEP 10: Enhanced Console Summary with Pandas ===
print("\n" + "="*80)
print("🔍 ENHANCED ANALYSIS SUMMARY WITH PANDAS TABLES")
print("="*80)

# Show quality metrics table in console
print("\n📊 CODE QUALITY METRICS:")
quality_console_table = create_quality_metrics_table(completion_analysis)
print(quality_console_table.to_string(index=False))

# Show file distribution summary
print("\n📁 CODEBASE DISTRIBUTION:")
total_lines_console = sum(doc.metadata["line_count"] for doc in documents)
summary_console_table = create_file_summary_table(file_breakdown, total_lines_console)
print(summary_console_table.to_string(index=False))

# Show top critical files
print("\n⭐ TOP 10 CRITICAL FILES:")
top_console_table = create_top_files_table(file_breakdown, top_n=10)
# Select key columns for console display
console_display = top_console_table[['File', 'Category', 'Lines', 'Functions', 'Importance', 'Critical']]
print(console_display.to_string(index=False))

print(f"\n📈 PROJECT COMPLETION: {completion_analysis['completion_percent']}%")
print(f"📊 TOTAL FILES: {len(documents)}")
print(f"📝 TOTAL LINES: {completion_analysis['total_lines']:,}")

critical_count = len([f for files in file_breakdown.values() for f in files if f['importance'] > 2])
print(f"⭐ CRITICAL COMPONENTS: {critical_count}")

print(f"\n🎉 Enhanced analysis complete! Check {OUTPUT_FILE} for full detailed report with all tables.")
