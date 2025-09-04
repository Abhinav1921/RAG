#!/usr/bin/env python3
"""
Deployment diagnostic script for the document analysis MCP server.
This script checks for common deployment issues and provides recommendations.
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Python Version Check")
    print(f"Current Python version: {sys.version}")
    
    if sys.version_info < (3, 11):
        print("❌ ERROR: Python 3.11+ required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_environment_variables():
    """Check required environment variables."""
    print("\n🔧 Environment Variables Check")
    
    # Load .env file if it exists
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file found")
        
        # Check for required variables
        required_vars = ['GOOGLE_API_KEY', 'MONGODB_CONNECTION_STRING']
        missing_vars = []
        
        with open(env_file) as f:
            content = f.read()
            
        for var in required_vars:
            if var not in content or f"{var}=your_" in content or f"{var}=AIzaSyExample" in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing or placeholder values for: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ Required environment variables are set")
            return True
    else:
        print("❌ .env file not found")
        return False

def check_dependencies():
    """Check if all dependencies can be imported."""
    print("\n📦 Dependencies Check")
    
    required_packages = [
        'pymongo',
        'langchain',
        'langchain_google_genai',
        'streamlit',
        'google.generativeai',
        'motor',
        'PyPDF2',
        'docx',
        'mcp'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def check_mongodb_connection():
    """Check MongoDB connection."""
    print("\n🗄️  MongoDB Connection Check")
    
    try:
        from services.document_mongodb_service import DocumentMongoDBService
        from services.embedding_service import EmbeddingService
        from dotenv import load_dotenv
        
        # Load environment variables first
        load_dotenv()
        
        # Create embedding service first
        embedding_service = EmbeddingService()
        
        # This will attempt to connect
        service = DocumentMongoDBService(embedding_service)
        print("✅ MongoDB service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def check_google_ai():
    """Check Google AI API."""
    print("\n🤖 Google AI API Check")
    
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key or api_key.startswith('your_'):
            print("❌ Google AI API key not properly configured")
            return False
            
        genai.configure(api_key=api_key)
        
        # Try to list models (lightweight API call)
        models = list(genai.list_models())
        print(f"✅ Google AI API working - {len(models)} models available")
        return True
    except Exception as e:
        print(f"❌ Google AI API failed: {e}")
        return False

def check_mcp_server():
    """Check MCP server can be imported and initialized."""
    print("\n🖥️  MCP Server Check")
    
    try:
        from main import server
        print("✅ MCP server imported successfully")
        
        # Check if it's a valid FastMCP instance
        if hasattr(server, 'name') and hasattr(server, 'list_tools'):
            print(f"✅ MCP server instance is valid (name: {server.name})")
        else:
            raise ValueError("Server is not a valid FastMCP instance")
        return True
    except Exception as e:
        print(f"❌ MCP server failed: {e}")
        return False

def check_streamlit_app():
    """Check Streamlit app can be imported."""
    print("\n🎯 Streamlit App Check")
    
    try:
        # Try to compile the Streamlit app without running it
        with open('document_streamlit_app.py', 'r', encoding='utf-8') as f:
            code = f.read()
            compile(code, 'document_streamlit_app.py', 'exec')
        
        print("✅ Streamlit app syntax is valid")
        return True
    except Exception as e:
        print(f"❌ Streamlit app failed: {e}")
        return False

def main():
    """Run all diagnostic checks."""
    print("🚀 Document Analysis MCP Server - Deployment Diagnostics")
    print("=" * 60)
    
    checks = [
        check_python_version,
        check_environment_variables,
        check_dependencies,
        check_mongodb_connection,
        check_google_ai,
        check_mcp_server,
        check_streamlit_app
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your deployment should work.")
    else:
        print("⚠️  Some checks failed. Please fix the issues above before deploying.")
        
        print("\n💡 Common Solutions:")
        print("   - Update environment variables in .env file")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Check MongoDB is running (for local deployment)")
        print("   - Verify Google AI API key is valid")

if __name__ == "__main__":
    main()
