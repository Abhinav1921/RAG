# Document Analysis MCP Server - Setup Guide

## ✅ Current Status
- ✅ Virtual environment created and activated
- ✅ All dependencies installed
- ✅ MongoDB connection working with local Compass instance
- ✅ Document processing tested successfully
- ✅ Sample documents created and ready

## 🔧 Final Setup Step: Google AI API Key

To enable AI-powered document analysis, you need a Google AI API key:

### 1. Get Your Google AI API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 2. Update Your .env File
Open the `.env` file and replace the placeholder:
```bash
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Test Everything Works
Run the complete test:
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'your_google_ai_api_key_here':
    print('✅ Google AI API key configured!')
else:
    print('❌ Please set your Google AI API key in .env file')
"
```

## 🚀 Running the Application

### Option 1: Streamlit Web Interface (Recommended)
```bash
# Make sure virtual environment is active
.\venv\Scripts\Activate.ps1

# Run the web app
streamlit run document_streamlit_app.py
```

### Option 2: Using the PowerShell Script
```bash
.\run_app.ps1
```

### Option 3: MCP Server
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run MCP server
mcp run main:server --port 8001
```

## 🎯 What You Can Do

1. **Upload Documents**: PDF, DOCX, TXT, MD files
2. **Ask Questions**: Natural language queries about your documents
3. **Semantic Search**: Find content based on meaning, not just keywords
4. **Multi-Document Support**: Search across multiple documents
5. **Source Attribution**: See exactly which document parts generated answers

## 📊 MongoDB Compass Integration

Your documents will be stored in:
- **Database**: `document_analysis`
- **Collection**: `document_chunks`

You can view the stored documents in MongoDB Compass:
1. Connect to `mongodb://localhost:27017`
2. Browse the `document_analysis` database
3. View the `document_chunks` collection

## 📝 Sample Queries to Try

Once you have the API key set up:
- "What are the remote work requirements?"
- "How do I create a new user via the API?"
- "What were the main action items from the engineering meeting?"
- "What security protocols should remote workers follow?"

## 🛠️ Troubleshooting

### MongoDB Issues
- Ensure MongoDB is running in Compass
- Check connection on `localhost:27017`
- Verify database permissions

### API Key Issues
- Verify the key is correctly set in `.env`
- Check for any extra spaces or quotes
- Test the key at Google AI Studio

### Import Errors
- Make sure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

## 📂 Project Structure
```
poc_mcp/
├── venv/                          # Virtual environment
├── sample_documents/              # Test documents
├── MCP/tools/document_tools.py    # Document MCP tools  
├── services/                      # Core services
├── database/                      # Data models
├── document_streamlit_app.py      # Web interface
├── .env                          # Your configuration
└── test_*.py                     # Test scripts
```

## 🎉 You're All Set!

Your document analysis system is ready to use with your local MongoDB Compass setup. The system will:
- Store documents locally in your MongoDB instance
- Use Google AI for embeddings and question answering
- Provide a user-friendly web interface for document interaction

Enjoy exploring your documents with AI-powered search! 🚀
