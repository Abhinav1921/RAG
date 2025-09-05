"""
Vercel API endpoint - Document Analysis MCP as API
Since Streamlit can't run on Vercel serverless, we'll create an API version.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import asyncio
from urllib.parse import parse_qs

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - serve the web interface."""
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Document Analysis MCP - API Version</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .container { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 10px 0; }
                .upload-area { border: 2px dashed #ccc; padding: 20px; text-align: center; }
                .chat-area { height: 400px; overflow-y: auto; background: white; padding: 15px; border-radius: 5px; }
                input[type="text"] { width: 80%; padding: 10px; }
                button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            </style>
        </head>
        <body>
            <h1>📄 Document Analysis MCP</h1>
            <p>AI-powered document analysis with semantic search</p>
            
            <div class="container">
                <h3>📁 Upload Document</h3>
                <div class="upload-area">
                    <input type="file" id="fileInput" accept=".txt,.md,.pdf,.docx">
                    <br><br>
                    <button onclick="uploadDocument()">🔄 Process Document</button>
                </div>
            </div>
            
            <div class="container">
                <h3>💬 Chat with Your Documents</h3>
                <div class="chat-area" id="chatArea">
                    <p>Upload a document first, then ask questions about it!</p>
                </div>
                <input type="text" id="queryInput" placeholder="Ask a question about your documents...">
                <button onclick="askQuestion()">Send</button>
            </div>
            
            <div class="container">
                <h3>🚀 For Full Features</h3>
                <p>This is a simplified API version. For the complete experience with file uploads and advanced features:</p>
                <a href="https://render.com" target="_blank">Deploy on Render</a> | 
                <a href="https://replit.com" target="_blank">Try on Replit</a> | 
                <a href="https://huggingface.co/spaces" target="_blank">Use Hugging Face Spaces</a>
            </div>
            
            <script>
                function uploadDocument() {
                    alert('File upload requires a full deployment on platforms like Render or Replit. This is a demo version.');
                }
                
                function askQuestion() {
                    const query = document.getElementById('queryInput').value;
                    if (!query) return;
                    
                    const chatArea = document.getElementById('chatArea');
                    chatArea.innerHTML += '<p><strong>You:</strong> ' + query + '</p>';
                    chatArea.innerHTML += '<p><strong>Assistant:</strong> To get AI responses, please deploy the full application on Render, Replit, or Hugging Face Spaces. This demo shows the interface only.</p>';
                    chatArea.scrollTop = chatArea.scrollHeight;
                    
                    document.getElementById('queryInput').value = '';
                }
                
                document.getElementById('queryInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') askQuestion();
                });
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def do_POST(self):
        """Handle POST requests - API endpoints."""
        
        # For demo purposes, return a JSON response
        response = {
            "message": "This is a demo API. For full functionality, deploy on Render, Replit, or Hugging Face Spaces.",
            "status": "demo",
            "platforms": [
                {"name": "Render", "url": "https://render.com", "recommended": True},
                {"name": "Replit", "url": "https://replit.com", "recommended": True},
                {"name": "Hugging Face", "url": "https://huggingface.co/spaces", "recommended": True}
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
