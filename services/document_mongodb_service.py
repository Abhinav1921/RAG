# services/document_mongodb_service.py
from database.models.document_chunk_model import DocumentChunk
from services.alternative_embedding_service import AlternativeEmbeddingService as EmbeddingService
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

class DocumentMongoDBService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.vector_index_name = os.getenv("VECTOR_INDEX_NAME", "vector_index")
        self.collection_name = os.getenv("COLLECTION_NAME", "document_chunks")
        print(f"DocumentMongoDBService initialized, targeting collection '{self.collection_name}' with vector index '{self.vector_index_name}'")

    async def find_chunks_by_semantic_search(self, query_text: str, document_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a semantic search on document chunks using Atlas Vector Search.
        Can optionally filter by document_id to search within a specific document.
        """
        print(f"Generating embedding for query: '{query_text}'")
        query_embedding = await self.embedding_service.get_embedding(query_text)
        print(f"Query embedding generated (first 5 dims): {query_embedding[:5]}...")

        # Build the pipeline with optional document filtering
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": limit,
                    "index": self.vector_index_name,
                }
            }
        ]
        
        # Add document filter if specified
        if document_id:
            pipeline.append({
                "$match": {"document_id": document_id}
            })
        
        # Add projection
        pipeline.append({
            "$project": {
                "_id": 0,
                "document_id": 1,
                "document_name": 1,
                "document_type": 1,
                "chunk_index": 1,
                "text_content": 1,
                "page_number": 1,
                "section_title": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        })

        print("Executing vector search pipeline...")
        
        try:
            # Get database and collection directly (cloud-safe)
            try:
                from database.cloud_connection import get_database
            except ImportError:
                from database.connection import get_database
            db = get_database()
            collection = db[self.collection_name]
            
            # Execute aggregation with proper cursor handling
            results = []
            async for doc in collection.aggregate(pipeline):
                results.append(doc)
            
            print(f"Vector search returned {len(results)} results.")
            return results
            
        except Exception as e:
            print(f"Error in vector search: {e}")
            
            # Fallback: Get documents and do basic filtering
            print("Falling back to simple document retrieval...")
            try:
                if document_id:
                    all_chunks = await DocumentChunk.find({"document_id": document_id}).to_list()
                else:
                    all_chunks = await DocumentChunk.find_all().to_list()
                
                # Simple text matching as fallback
                filtered_chunks = []
                query_lower = query_text.lower()
                
                for chunk in all_chunks:
                    if any(word in chunk.text_content.lower() for word in query_lower.split()):
                        filtered_chunks.append({
                            "document_id": chunk.document_id,
                            "document_name": chunk.document_name,
                            "document_type": chunk.document_type,
                            "chunk_index": chunk.chunk_index,
                            "text_content": chunk.text_content,
                            "page_number": chunk.page_number,
                            "section_title": chunk.section_title,
                            "score": 0.5  # Default score
                        })
                
                # Limit results
                filtered_chunks = filtered_chunks[:limit]
                print(f"Fallback search returned {len(filtered_chunks)} results.")
                return filtered_chunks
                
            except Exception as fallback_error:
                print(f"Fallback search also failed: {fallback_error}")
                return []

    async def insert_document_chunk(self, chunk_data: Dict[str, Any]) -> DocumentChunk:
        """Inserts a single document chunk into the database."""
        # Add timestamp if not provided
        if 'timestamp' not in chunk_data:
            chunk_data['timestamp'] = datetime.utcnow()
            
        new_chunk = DocumentChunk(**chunk_data)
        await new_chunk.insert()
        print(f"Inserted chunk {new_chunk.chunk_index} for document {new_chunk.document_name}")
        return new_chunk

    async def insert_document_chunks_batch(self, chunks: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """Inserts multiple document chunks in batch."""
        document_chunks = []
        for chunk_data in chunks:
            if 'timestamp' not in chunk_data:
                chunk_data['timestamp'] = datetime.utcnow()
            document_chunks.append(DocumentChunk(**chunk_data))
        
        if document_chunks:
            await DocumentChunk.insert_many(document_chunks)
            print(f"Inserted {len(document_chunks)} chunks in batch")
        
        return document_chunks

    async def get_all_chunks(self, document_id: Optional[str] = None) -> List[DocumentChunk]:
        """Retrieves all document chunks, optionally filtered by document_id."""
        if document_id:
            return await DocumentChunk.find({"document_id": document_id}).to_list()
        return await DocumentChunk.find_all().to_list()

    async def get_documents_list(self) -> List[Dict[str, Any]]:
        """Get a list of all unique documents in the database."""
        try:
            # Use cloud-safe database getter
            try:
                from database.cloud_connection import get_database
            except ImportError:
                from database.connection import get_database
            db = get_database()
            collection = db[self.collection_name]
            
            # Aggregate to get unique documents
            pipeline = [
                {
                    "$group": {
                        "_id": "$document_id",
                        "document_name": {"$first": "$document_name"},
                        "document_type": {"$first": "$document_type"},
                        "chunk_count": {"$sum": 1},
                        "last_updated": {"$max": "$timestamp"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "document_id": "$_id",
                        "document_name": 1,
                        "document_type": 1,
                        "chunk_count": 1,
                        "last_updated": 1
                    }
                }
            ]
            
            results = []
            async for doc in collection.aggregate(pipeline):
                results.append(doc)
            
            return results
            
        except Exception as e:
            print(f"Error getting documents list: {e}")
            return []

    async def delete_document(self, document_id: str) -> int:
        """Delete all chunks for a specific document."""
        try:
            result = await DocumentChunk.find({"document_id": document_id}).delete()
            print(f"Deleted {result.deleted_count} chunks for document {document_id}")
            return result.deleted_count
        except Exception as e:
            print(f"Error deleting document {document_id}: {e}")
            return 0
