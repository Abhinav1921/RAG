#!/usr/bin/env python3
"""
Main entry point for both MCP server and web deployment.
Railway/cloud platforms automatically detect and run this file.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Import MCP server components
from MCP.tools.document_tools import app as document_mcp_server
server = document_mcp_server

def run_streamlit_app():
    """Run the Streamlit application for web deployment."""
    
    # Get the port from environment (Railway/Heroku set this)
    port = os.environ.get("PORT", "8080")
    
    # Run Streamlit with cloud deployment configuration
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "document_streamlit_app.py",
        "--server.port=" + port,
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ]
    
    print(f"🚀 Starting Streamlit app on port {port}")
    print(f"Command: {' '.join(cmd)}")
    
    # Run the application
    subprocess.run(cmd)

def run_mcp_server():
    """Run the MCP server for local development."""
    print("Hello from poc-mcp! (This message is from your main() function).")
    print("To start the MCP server, you MUST use the command: `mcp run main:server --port 8001`.")
    print("This main() function does not start the MCP server itself.")

if __name__ == "__main__":
    # Check if we're in a web deployment environment
    if os.environ.get("PORT") or os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RENDER") or os.environ.get("RENDER_SERVICE_NAME"):
        # Web deployment - run Streamlit
        print("Detected web deployment environment - starting Streamlit app")
        run_streamlit_app()
    else:
        # Local development - show MCP server info
        run_mcp_server()
    