# Document Analysis MCP Server

A powerful Document Analysis system using the Model Control Protocol (MCP) that allows you to upload documents and ask questions about them using natural language. The system provides semantic search capabilities and AI-powered answers based on document content.

## Features

- 📄 **Multi-format Support**: Upload PDF, DOCX, TXT, and Markdown files
- 🔍 **Semantic Search**: Find relevant content based on meaning, not just keywords
- 🤖 **AI-Powered Q&A**: Get intelligent answers using Google's Gemini model
- 📚 **Multi-Document Support**: Search across multiple documents or within specific ones
- ⚡ **Fast Processing**: Efficient document chunking and vector embeddings
- 🎯 **Source Attribution**: See exactly which document sections generated each answer
- 💾 **MongoDB Atlas**: Scalable vector search with Atlas Search
- 🖥️ **Streamlit Interface**: Easy-to-use web interface for document upload and querying
- 🔧 **MCP Integration**: Compatible with MCP-enabled clients

## Architecture

### Core Components
1. **Document Processing Service**: Extracts text from various file formats
2. **Embedding Service**: Generates vector embeddings using Google AI
3. **MongoDB Service**: Handles vector search and document storage
4. **MCP Tools**: Provides document upload and search functionality
5. **Streamlit App**: Web interface for easy interaction

### Workflow
1. Upload document → Extract text → Split into chunks → Generate embeddings → Store in MongoDB
2. User query → Generate query embedding → Vector search → Retrieve relevant chunks → Generate AI answer

## Setup

### Prerequisites
- Python 3.13+
- MongoDB Atlas account with vector search enabled
- Google AI API key

### Installation

1. **Clone and install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables** (create `.env` file):
```bash
MONGODB_CONNECTION_STRING=your_mongodb_atlas_connection_string
GOOGLE_API_KEY=your_google_ai_api_key
COLLECTION_NAME=document_chunks
VECTOR_INDEX_NAME=vector_index
```

3. **Create sample documents** (optional):
```bash
python scripts/create_sample_documents.py
```

## Usage

### Streamlit Web Interface
```bash
streamlit run document_streamlit_app.py
```

### MCP Server
```bash
mcp run main:server --port 8001
```

### Available MCP Tools

1. **upload_and_process_document**
   - Upload and process a document file
   - Supports: PDF, DOCX, DOC, TXT, MD
   - Parameters: file_path, chunk_size, overlap

2. **search_documents** 
   - Search through documents using natural language
   - Parameters: query_text, document_id (optional), limit

3. **list_documents**
   - Get list of all uploaded documents
   - Returns: document metadata and statistics

4. **delete_document**
   - Remove a document and all its chunks
   - Parameters: document_id

## File Format Support

| Format | Extension | Requirements |
|--------|-----------|-------------|
| Text | .txt, .md | Built-in |
| PDF | .pdf | `pip install PyPDF2` |
| Word | .docx, .doc | `pip install python-docx` |

## MongoDB Atlas Setup

1. Create a MongoDB Atlas cluster
2. Create a database and collection (name specified in COLLECTION_NAME env var)
3. Create a vector search index on the `embedding` field:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    }
  ]
}
```

## Example Queries

- "What are the remote work requirements?"
- "How do I create a new user via the API?"
- "What were the main action items from the engineering meeting?"
- "What security protocols should remote workers follow?"
- "Show me the API endpoints for user management"

## Development

### Project Structure
```
poc_mcp/
├── MCP/tools/document_tools.py          # MCP tool implementations
├── database/
│   ├── models/document_chunk_model.py   # Document chunk data model
│   └── connection.py                    # Database connection
├── services/
│   ├── document_processing_service.py   # Document text extraction
│   ├── document_mongodb_service.py      # MongoDB operations
│   └── embedding_service.py             # Vector embedding generation
├── scripts/
│   └── create_sample_documents.py       # Sample data creation
├── document_streamlit_app.py            # Web interface
├── main.py                              # MCP server entry point
└── requirements.txt                     # Dependencies
```

### Adding New Document Types

1. Update `DocumentProcessingService.supported_extensions`
2. Add extraction method in `DocumentProcessingService`
3. Install required dependencies
4. Update requirements.txt and pyproject.toml

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**: Check connection string and network access
2. **Vector Search Not Working**: Ensure vector index is created correctly
3. **Document Processing Fails**: Check file format support and dependencies
4. **Embedding Generation Fails**: Verify Google AI API key

### Performance Optimization

- Adjust chunk_size and overlap based on document type
- Use appropriate MongoDB index settings
- Consider batch processing for large documents
- Monitor vector search performance metrics

## Contributing

This is an internship project demonstrating document analysis capabilities using modern AI/ML technologies and the MCP protocol.

## Tech Stack

- **Python 3.13+**
- **FastMCP**: MCP server framework
- **MongoDB Atlas**: Document storage and vector search
- **Google AI**: Embeddings and LLM (Gemini)
- **LangChain**: AI orchestration
- **Streamlit**: Web interface
- **Beanie**: MongoDB ODM
- **PyPDF2**: PDF processing
- **python-docx**: Word document processing
