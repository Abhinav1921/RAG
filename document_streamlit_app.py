import streamlit as st
import json
import os
import asyncio
import sys
from dotenv import load_dotenv
from pathlib import Path
import tempfile

# Load environment variables (fallback to .env for local development)
try:
    # Try to use Streamlit secrets first (for cloud deployment)
    if hasattr(st, 'secrets') and st.secrets:
        for key, value in st.secrets["secrets"].items():
            os.environ[key] = str(value)
    else:
        # Fallback to .env file for local development
        load_dotenv()
except Exception:
    # Fallback to .env file if secrets are not available
    load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(__file__))

# Import document-based MCP components
from MCP.tools.document_tools import (
    upload_and_process_document_sync,
    search_documents_sync,
    list_documents_sync
)
# Import both connection methods
try:
    from database.cloud_connection import connect_db_cloud_safe as connect_db
    from database.cloud_connection import get_database
except ImportError:
    from database.connection import connect_db, get_database
from database.models.document_chunk_model import DocumentChunk

st.set_page_config(
    page_title="Document Analysis MCP Chat", 
    layout="wide",
    page_icon="📄"
)

st.title("📄 Document Analysis MCP Chat")
st.markdown("Upload documents and ask questions about them using natural language. Supports PDF, DOCX, TXT, and MD files.")

# Initialize database connection (cached to avoid reconnecting)
@st.cache_resource
def init_database():
    """Initialize database connection synchronously"""
    try:
        # Create a dedicated event loop for database initialization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(connect_db(document_models=[DocumentChunk]))
            return True
        finally:
            # Don't close the loop here as it might be needed later
            pass
    except Exception as e:
        error_msg = str(e)
        st.error(f"Database connection failed: {error_msg}")
        
        # Provide specific help for SSL issues
        if "ssl" in error_msg.lower() or "tls" in error_msg.lower():
            st.error("🔧 SSL/TLS Connection Issue Detected!")
            st.info("""
            **This is a common issue with cloud deployments. Here's how to fix it:**
            
            1. **Check MongoDB Atlas Settings:**
               - Go to Network Access → Add IP Address → Allow Access from Anywhere (0.0.0.0/0)
               - Verify your cluster is running (not paused)
            
            2. **Connection String Format:**
               - Make sure it starts with `mongodb+srv://`
               - Verify username and password are correct
            
            3. **Try Restarting the App:**
               - Sometimes a simple restart fixes SSL handshake issues
            """)
            
        return False

# Initialize DB
if not init_database():
    st.stop()

# Sidebar for document management
with st.sidebar:
    st.header("📁 Document Management")
    
    # Document upload section
    st.subheader("Upload New Document")
    uploaded_file = st.file_uploader(
        "Choose a document file",
        type=['txt', 'md', 'pdf', 'docx', 'doc'],
        help="Supported formats: TXT, MD, PDF, DOCX, DOC"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.number_input("Chunk Size", min_value=500, max_value=2000, value=1000, step=100)
    with col2:
        overlap = st.number_input("Overlap", min_value=50, max_value=500, value=200, step=50)
    
    if uploaded_file is not None:
        if st.button("🔄 Process Document", type="primary"):
            with st.spinner("Processing document..."):
                # Save uploaded file to temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                try:
                    # Process the document
                    result = upload_and_process_document_sync(
                        file_path=tmp_file_path,
                        chunk_size=chunk_size,
                        overlap=overlap
                    )
                    
                    if result.get("success"):
                        st.success(f"✅ {result['message']}")
                        st.info(f"Created {result['chunks_created']} chunks")
                        # Clear the file uploader by rerunning
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                        
                except Exception as e:
                    st.error(f"❌ Error processing document: {str(e)}")
                
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass
    
    # Document list section
    st.subheader("📚 Stored Documents")
    
    if st.button("🔄 Refresh Document List"):
        st.cache_resource.clear()
    
    # Get and display document list
    with st.spinner("Loading documents..."):
        docs_result = list_documents_sync()
        
        if docs_result.get("success") and docs_result.get("documents"):
            documents = docs_result["documents"]
            st.write(f"**Total Documents:** {len(documents)}")
            
            for doc in documents:
                with st.container():
                    st.write(f"**📄 {doc['document_name']}**")
                    st.caption(f"Type: {doc['document_type']} | Chunks: {doc['chunk_count']} | ID: {doc['document_id'][:8]}...")
                    
                    # Option to search within this specific document
                    if st.button(f"🎯 Search in this document", key=f"search_{doc['document_id']}"):
                        st.session_state['selected_document_id'] = doc['document_id']
                        st.session_state['selected_document_name'] = doc['document_name']
                        st.rerun()
                    
                    st.divider()
        else:
            st.info("No documents uploaded yet. Upload a document to get started!")

# Main chat interface
st.header("💬 Chat with Your Documents")

# Document filter selection
document_filter_options = ["All Documents"]
selected_doc_name = "All Documents"

# Check if a specific document was selected from sidebar
if 'selected_document_id' in st.session_state:
    selected_doc_name = st.session_state['selected_document_name']
    st.info(f"🎯 Searching within: **{selected_doc_name}**")
    
    if st.button("🔄 Search All Documents"):
        if 'selected_document_id' in st.session_state:
            del st.session_state['selected_document_id']
        if 'selected_document_name' in st.session_state:
            del st.session_state['selected_document_name']
        st.rerun()

# Chat History Management
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "retrieved_chunks" in message and message["retrieved_chunks"]:
            with st.expander("📖 Retrieved Context"):
                for chunk in message["retrieved_chunks"]:
                    st.write(f"**Document:** {chunk.get('document_name', 'N/A')}")
                    st.write(f"**Chunk:** {chunk.get('chunk_index', 'N/A')}")
                    if chunk.get('page_number'):
                        st.write(f"**Page:** {chunk.get('page_number')}")
                    st.markdown(f"**Content:** {chunk.get('text_content', 'N/A')}")
                    st.markdown(f"**Relevance Score:** {chunk.get('score', 'N/A'):.4f}")
                    st.markdown("---")
        
        if "source_documents" in message and message["source_documents"]:
            with st.expander("📚 Source Documents"):
                for doc in message["source_documents"]:
                    st.write(f"• {doc}")

# User Input and Document Search
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Determine document_id filter
                document_id = st.session_state.get('selected_document_id', None)
                
                # Call document search function
                result = search_documents_sync(
                    query_text=prompt, 
                    document_id=document_id, 
                    limit=5
                )
                
                if result and result.answer:
                    answer = result.answer
                    retrieved_chunks = [chunk.model_dump() for chunk in result.retrieved_chunks]
                    source_documents = result.source_documents

                    st.markdown(answer)
                    
                    # Show retrieved context
                    if retrieved_chunks:
                        with st.expander("📖 Retrieved Context"):
                            for chunk in retrieved_chunks:
                                st.write(f"**Document:** {chunk.get('document_name', 'N/A')}")
                                st.write(f"**Chunk:** {chunk.get('chunk_index', 'N/A')}")
                                if chunk.get('page_number'):
                                    st.write(f"**Page:** {chunk.get('page_number')}")
                                st.markdown(f"**Content:** {chunk.get('text_content', 'N/A')}")
                                st.markdown(f"**Relevance Score:** {chunk.get('score', 'N/A'):.4f}")
                                st.markdown("---")
                    
                    # Show source documents
                    if source_documents:
                        with st.expander("📚 Source Documents"):
                            for doc in source_documents:
                                st.write(f"• {doc}")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "retrieved_chunks": retrieved_chunks,
                        "source_documents": source_documents
                    })
                else:
                    error_msg = "Failed to get results from the document search."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                # Optional: Show detailed error for debugging
                with st.expander("Debug Info"):
                    st.exception(e)

# Instructions/Help
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    ### Getting Started:
    1. **Upload a document** using the sidebar file uploader
    2. **Wait for processing** - the document will be split into chunks and stored
    3. **Ask questions** about your documents in natural language
    
    ### Supported File Types:
    - **PDF** (.pdf) - Requires PyPDF2: `pip install PyPDF2`
    - **Word Documents** (.docx, .doc) - Requires python-docx: `pip install python-docx`
    - **Text Files** (.txt, .md) - No additional requirements
    
    ### Features:
    - **Semantic Search**: Find relevant content based on meaning, not just keywords
    - **Multi-Document Support**: Upload multiple documents and search across all of them
    - **Document-Specific Search**: Filter search to a specific document
    - **Context Display**: See the exact text chunks that were used to generate answers
    - **Source Attribution**: Know which documents your answers came from
    
    ### Tips:
    - **Ask specific questions** for better results
    - **Use natural language** - no need for keywords
    - **Check the context** to understand how answers were generated
    - **Experiment with chunk size** and overlap for different document types
    """)

# Footer
st.markdown("---")
st.caption("Powered by Document Analysis MCP Server | Built with Streamlit, MongoDB Atlas, and Google AI")
