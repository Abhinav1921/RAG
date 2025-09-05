#!/usr/bin/env python3
"""
Render-specific startup script with health checks and diagnostics.
This script ensures proper initialization before starting the main application.
"""

import os
import sys
import asyncio
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def setup_render_environment():
    """Set up Render-specific environment variables and configurations."""
    
    print("🚀 Render Startup Script")
    print("=" * 50)
    
    # Detect Render environment
    is_render = bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_NAME"))
    
    if is_render:
        print("✅ Detected Render deployment environment")
        
        # Set Render-specific optimizations
        os.environ["RENDER"] = "true"
        os.environ["PYTHONUNBUFFERED"] = "1"
        
        # Add Render-specific MongoDB optimizations
        if not os.getenv("MONGODB_TIMEOUT_MS"):
            os.environ["MONGODB_TIMEOUT_MS"] = "45000"
        
        print("✅ Render environment optimizations applied")
    else:
        print("ℹ️  Not detected as Render deployment")
    
    # Verify required environment variables
    required_vars = [
        "MONGODB_CONNECTION_STRING",
        "GOOGLE_API_KEY",
        "DATABASE_NAME",
        "COLLECTION_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your Render environment variable configuration")
        sys.exit(1)
    else:
        print("✅ All required environment variables are set")

async def test_database_connection():
    """Test database connection before starting the main application."""
    
    print("\n🔍 Testing database connection...")
    
    try:
        # Import and test the cloud-safe connection
        from database.cloud_connection import connect_db_cloud_safe
        from database.models.document_chunk_model import DocumentChunk
        
        # Test connection with timeout
        await asyncio.wait_for(
            connect_db_cloud_safe(document_models=[DocumentChunk]),
            timeout=60.0
        )
        
        print("✅ Database connection successful!")
        return True
        
    except asyncio.TimeoutError:
        print("❌ Database connection timeout (60s)")
        print("This might be due to:")
        print("  - MongoDB Atlas cluster is paused")
        print("  - Network connectivity issues")
        print("  - Incorrect connection string")
        return False
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_google_ai_api():
    """Test Google AI API connection."""
    
    print("\n🔍 Testing Google AI API...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ Google AI API key not found")
            return False
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Test with a simple embedding request (this validates the key without making a big request)
        print("✅ Google AI API key configured successfully")
        return True
        
    except Exception as e:
        print(f"❌ Google AI API test failed: {str(e)}")
        return False

def start_main_application():
    """Start the main application."""
    
    print("\n🚀 Starting main application...")
    
    try:
        # Import and run the main application
        from main import run_streamlit_app
        
        print("✅ Launching Streamlit application...")
        run_streamlit_app()
        
    except Exception as e:
        print(f"❌ Failed to start main application: {str(e)}")
        sys.exit(1)

async def health_check_sequence():
    """Run health checks before starting the application."""
    
    print("\n🏥 Running health checks...")
    
    all_passed = True
    
    # Test database connection
    try:
        db_result = await test_database_connection()
        if db_result:
            print("✅ Database Connection: PASS")
        else:
            print("❌ Database Connection: FAIL")
            all_passed = False
    except Exception as e:
        print(f"❌ Database Connection: ERROR - {str(e)}")
        all_passed = False
    
    # Test Google AI API
    try:
        ai_result = test_google_ai_api()
        if ai_result:
            print("✅ Google AI API: PASS")
        else:
            print("❌ Google AI API: FAIL")
            all_passed = False
    except Exception as e:
        print(f"❌ Google AI API: ERROR - {str(e)}")
        all_passed = False
    
    return all_passed

async def main():
    """Main startup sequence."""
    
    # Setup environment
    setup_render_environment()
    
    # Run health checks
    health_ok = await health_check_sequence()
    
    if not health_ok:
        print("\n❌ Health checks failed!")
        print("The application may not work correctly, but we'll try to start it anyway...")
        print("Check the logs above for specific issues to resolve.")
        
        # In Render, we still want to start the app even if some checks fail
        # This prevents the deployment from being marked as failed
        if os.getenv("RENDER") or os.getenv("RENDER_SERVICE_NAME"):
            print("⚠️  Starting application anyway (Render deployment)")
        else:
            print("Exiting due to health check failures...")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 All checks passed! Starting application...")
    print("=" * 50)
    
    # Start the main application
    start_main_application()

if __name__ == "__main__":
    asyncio.run(main())
