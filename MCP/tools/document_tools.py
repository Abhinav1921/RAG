# MCP/tools/document_tools.py

import sys
import os

# Modern MCP approach using FastMCP
from mcp.server.fastmcp import FastMCP

from services.document_mongodb_service import DocumentMongoDBService
from services.alternative_embedding_service import AlternativeEmbeddingService as EmbeddingService
from services.document_processing_service import DocumentProcessingService
from database.connection import connect_db
from database.models.document_chunk_model import DocumentChunk
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import asyncio
import concurrent.futures

# --- Global service instances (lazy-loaded) ---
embedding_service_instance = None
document_mongodb_service_instance = None
document_processing_service_instance = None

def get_services():
    """Lazy-load services to avoid environment variable issues at import time"""
    global embedding_service_instance, document_mongodb_service_instance, document_processing_service_instance
    
    if embedding_service_instance is None:
        from dotenv import load_dotenv
        load_dotenv()  # Ensure environment variables are loaded
        
        embedding_service_instance = EmbeddingService()
        document_mongodb_service_instance = DocumentMongoDBService(embedding_service_instance)
        document_processing_service_instance = DocumentProcessingService()
    
    return embedding_service_instance, document_mongodb_service_instance, document_processing_service_instance

# --- Create FastMCP Server ---
app = FastMCP("Document Analysis MCP Server")

# --- Input/Output Schemas ---
class DocumentUploadInput(BaseModel):
    file_path: str = Field(..., description="Path to the document file to upload and process")
    chunk_size: int = Field(1000, description="Size of text chunks for processing")
    overlap: int = Field(200, description="Overlap between chunks")

class DocumentSearchInput(BaseModel):
    query_text: str = Field(..., description="The natural language query for finding relevant document content")
    document_id: Optional[str] = Field(None, description="Optional document ID to search within a specific document")
    limit: int = Field(5, description="Maximum number of relevant chunks to retrieve")

class RetrievedDocumentChunk(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    chunk_index: int
    text_content: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    score: float

class DocumentSearchResult(BaseModel):
    answer: str = Field(..., description="The AI-generated answer based on the retrieved document context")
    retrieved_chunks: List[RetrievedDocumentChunk] = Field(..., description="List of document chunks used to generate the answer")
    source_documents: List[str] = Field(..., description="List of source document names")

class DocumentInfo(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    chunk_count: int
    last_updated: str

# --- MCP Tool Implementations ---

@app.tool()
async def upload_and_process_document(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> dict:
    """
    Upload and process a document file, extracting text and storing it in chunks with embeddings.
    
    Args:
        file_path: Path to the document file (supports .txt, .md, .pdf, .docx)
        chunk_size: Size of text chunks for processing (default: 1000)
        overlap: Overlap between chunks (default: 200)
    
    Returns:
        Dictionary with processing results
    """
    print(f"Processing document: {file_path}")
    
    try:
        # Get lazy-loaded services
        embedding_service, mongodb_service, processing_service = get_services()
        
        # Process the document
        document_id, document_name, chunks = await processing_service.process_document(
            file_path, chunk_size, overlap
        )
        
        print(f"Document processed: {document_name} ({len(chunks)} chunks)")
        
        # Generate embeddings and store chunks
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}")
            try:
                chunk['embedding'] = await embedding_service.get_embedding(chunk['text_content'])
                print(f"Successfully generated embedding for chunk {i+1}")
            except Exception as embed_error:
                print(f"Error generating embedding for chunk {i+1}: {embed_error}")
                raise
        
        # Store chunks in database
        try:
            await mongodb_service.insert_document_chunks_batch(chunks)
            print(f"Successfully stored {len(chunks)} chunks in database")
        except Exception as db_error:
            print(f"Error storing chunks in database: {db_error}")
            raise
        
        return {
            "success": True,
            "message": f"Successfully processed and stored document: {document_name}",
            "document_id": document_id,
            "document_name": document_name,
            "chunks_created": len(chunks)
        }
        
    except Exception as e:
        print(f"Error processing document: {e}")
        return {
            "success": False,
            "message": f"Error processing document: {str(e)}",
            "document_id": None,
            "document_name": None,
            "chunks_created": 0
        }

@app.tool()
async def search_documents(query_text: str, document_id: Optional[str] = None, limit: int = 5) -> dict:
    """
    Search through document chunks using semantic search and generate an answer using an LLM.
    
    Args:
        query_text: The natural language query for finding relevant document content
        document_id: Optional document ID to search within a specific document
        limit: Maximum number of relevant chunks to retrieve (default: 5)
    
    Returns:
        Dictionary with answer and retrieved chunks
    """
    print(f"Searching documents with query: '{query_text}'")
    if document_id:
        print(f"Filtering by document_id: {document_id}")
    
    # Get lazy-loaded services
    embedding_service, mongodb_service, processing_service = get_services()
    
    # Perform semantic search
    retrieved_docs_raw = await mongodb_service.find_chunks_by_semantic_search(
        query_text=query_text,
        document_id=document_id,
        limit=limit
    )
    
    if not retrieved_docs_raw:
        print("No relevant chunks found.")
        return {
            "answer": "I could not find any relevant information in the documents for your query.",
            "retrieved_chunks": [],
            "source_documents": []
        }
    
    retrieved_chunks_models = [RetrievedDocumentChunk(**doc) for doc in retrieved_docs_raw]
    
    # Get unique source documents
    source_documents = list(set([chunk.document_name for chunk in retrieved_chunks_models]))
    
    # Create context for LLM
    context_string = "\n---\n".join([
        f"Document: {chunk.document_name}\nChunk {chunk.chunk_index}: {chunk.text_content}"
        for chunk in retrieved_chunks_models
    ])
    print(f"Context provided to LLM:\n{context_string[:500]}..." if len(context_string) > 500 else context_string)
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Create context from documents
        context = "\n\n".join([doc['text_content'] for doc in retrieved_docs_raw])
        
        # Create prompt template
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""Based on the following document context, please answer the question.

Context:
{context}

Question: {question}

Answer:"""
        )
        
        # Create the prompt and invoke
        prompt = prompt_template.format(context=context, question=query_text)
        response = await llm.ainvoke(prompt)
        generated_answer = response.content if hasattr(response, 'content') else str(response)
        
        print(f"Generated answer: {generated_answer}")
        
        return {
            "answer": generated_answer,
            "retrieved_chunks": [chunk.model_dump() for chunk in retrieved_chunks_models],
            "source_documents": source_documents
        }
        
    except Exception as e:
        print(f"Error during LLM generation: {e}")
        return {
            "answer": f"An error occurred while generating the answer: {str(e)}",
            "retrieved_chunks": [chunk.model_dump() for chunk in retrieved_chunks_models],
            "source_documents": source_documents
        }

@app.tool()
async def list_documents() -> dict:
    """
    Get a list of all documents stored in the system.
    
    Returns:
        Dictionary with list of documents and their metadata
    """
    print("Retrieving documents list...")
    
    try:
        # Get lazy-loaded services
        embedding_service, mongodb_service, processing_service = get_services()
        
        documents = await mongodb_service.get_documents_list()
        
        document_list = []
        for doc in documents:
            document_list.append({
                "document_id": doc["document_id"],
                "document_name": doc["document_name"],
                "document_type": doc["document_type"],
                "chunk_count": doc["chunk_count"],
                "last_updated": doc["last_updated"].isoformat() if doc["last_updated"] else None
            })
        
        return {
            "success": True,
            "documents": document_list,
            "total_documents": len(document_list)
        }
        
    except Exception as e:
        print(f"Error retrieving documents list: {e}")
        return {
            "success": False,
            "documents": [],
            "total_documents": 0,
            "error": str(e)
        }

@app.tool()
async def delete_document(document_id: str) -> dict:
    """
    Delete a document and all its chunks from the system.
    
    Args:
        document_id: The ID of the document to delete
    
    Returns:
        Dictionary with deletion results
    """
    print(f"Deleting document: {document_id}")
    
    try:
        # Get lazy-loaded services
        embedding_service, mongodb_service, processing_service = get_services()
        
        deleted_count = await mongodb_service.delete_document(document_id)
        
        if deleted_count > 0:
            return {
                "success": True,
                "message": f"Successfully deleted document with {deleted_count} chunks",
                "deleted_chunks": deleted_count
            }
        else:
            return {
                "success": False,
                "message": f"No document found with ID: {document_id}",
                "deleted_chunks": 0
            }
            
    except Exception as e:
        print(f"Error deleting document: {e}")
        return {
            "success": False,
            "message": f"Error deleting document: {str(e)}",
            "deleted_chunks": 0
        }

# --- Synchronous Wrappers for Streamlit ---

def upload_and_process_document_sync(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> dict:
    """Synchronous wrapper for document upload"""
    try:
        def run_in_new_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                new_loop.run_until_complete(connect_db(document_models=[DocumentChunk]))
                return new_loop.run_until_complete(
                    upload_and_process_document(file_path=file_path, chunk_size=chunk_size, overlap=overlap)
                )
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_thread)
            result = future.result(timeout=300)  # 5 minute timeout for document processing
            return result
                
    except Exception as e:
        print(f"Error in upload sync wrapper: {e}")
        return {
            "success": False,
            "message": f"An error occurred while processing document: {str(e)}",
            "document_id": None,
            "document_name": None,
            "chunks_created": 0
        }

def search_documents_sync(query_text: str, document_id: Optional[str] = None, limit: int = 5) -> DocumentSearchResult:
    """Synchronous wrapper for document search"""
    try:
        def run_in_new_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                new_loop.run_until_complete(connect_db(document_models=[DocumentChunk]))
                return new_loop.run_until_complete(
                    search_documents(query_text=query_text, document_id=document_id, limit=limit)
                )
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_thread)
            result = future.result(timeout=60)  # 60 second timeout
            
            # Convert dict result to DocumentSearchResult
            retrieved_chunks = [RetrievedDocumentChunk(**chunk) for chunk in result.get("retrieved_chunks", [])]
            return DocumentSearchResult(
                answer=result.get("answer", ""),
                retrieved_chunks=retrieved_chunks,
                source_documents=result.get("source_documents", [])
            )
                
    except Exception as e:
        print(f"Error in search sync wrapper: {e}")
        return DocumentSearchResult(
            answer=f"An error occurred while searching: {str(e)}",
            retrieved_chunks=[],
            source_documents=[]
        )

def list_documents_sync() -> dict:
    """Synchronous wrapper for listing documents"""
    try:
        def run_in_new_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                new_loop.run_until_complete(connect_db(document_models=[DocumentChunk]))
                return new_loop.run_until_complete(list_documents())
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_thread)
            return future.result(timeout=30)
                
    except Exception as e:
        print(f"Error in list sync wrapper: {e}")
        return {
            "success": False,
            "documents": [],
            "total_documents": 0,
            "error": str(e)
        }

# --- Database Initialization Function ---
async def initialize_database():
    """Initialize database connection"""
    print("Initializing database connection...")
    await connect_db(document_models=[DocumentChunk])
    print("MongoDB connection established.")
