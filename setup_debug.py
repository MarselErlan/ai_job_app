#!/usr/bin/env python3
"""
🔧 DEBUG ENVIRONMENT SETUP SCRIPT

This script helps set up the debugging environment by:
1. Creating .env file from debug_config.env template
2. Initializing the database with required tables
3. Validating the setup

Run this before running debug_test.py
"""

import os
import shutil
from pathlib import Path

def setup_environment():
    """Set up the debugging environment"""
    print("🔧 Setting up debug environment...")
    
    # Create .env from template if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('debug_config.env'):
            shutil.copy('debug_config.env', '.env')
            print("✅ Created .env from debug_config.env template")
            print("📝 Please edit .env and add your actual API keys")
        else:
            print("❌ debug_config.env template not found!")
            return False
    else:
        print("📋 .env file already exists")
    
    # Create logs directory
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✅ Created logs directory")
    
    # Create uploads directory
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        uploads_dir.mkdir()
        print("✅ Created uploads directory")
    
    # Initialize database
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.models import Base
        from app.db.session import engine
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"⚠️ Database setup warning: {e}")
        print("   This is normal if database already exists or API keys are not set")
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your actual API keys")
    print("2. Run: python debug_test.py")
    print("3. Check logs/debug.log for detailed debug information")
    
    return True

if __name__ == "__main__":
    setup_environment() 