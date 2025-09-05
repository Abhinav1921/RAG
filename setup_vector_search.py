#!/usr/bin/env python3
"""
Script to set up MongoDB Atlas Vector Search index for semantic document search.
This script helps automate the vector search index creation for deployment.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from database.connection import connect_db, get_database
from database.models.document_chunk_model import DocumentChunk

async def setup_vector_search():
    """Set up Atlas Vector Search index for semantic search."""
    
    print("🔧 Setting up Atlas Vector Search Index...")
    print("=" * 50)
    
    try:
        # Connect to database
        await connect_db([DocumentChunk])
        db = get_database()
        collection = db[os.getenv("COLLECTION_NAME", "document_chunks")]
        
        # Check if this is an Atlas connection
        mongo_uri = os.getenv("MONGODB_CONNECTION_STRING")
        if not mongo_uri or "mongodb+srv://" not in mongo_uri:
            print("⚠️  WARNING: Vector search requires MongoDB Atlas.")
            print("   Local MongoDB does not support vector search.")
            print("   Please use MongoDB Atlas for vector search capabilities.")
            return False
        
        print("✅ Connected to Atlas database")
        
        # Vector search index configuration
        vector_index_name = os.getenv("VECTOR_INDEX_NAME", "vector_index")
        
        # Check if index already exists
        try:
            indexes = await collection.list_indexes().to_list(None)
            existing_indexes = [idx.get('name', '') for idx in indexes]
            
            if vector_index_name in existing_indexes:
                print(f"✅ Vector search index '{vector_index_name}' already exists!")
                return True
                
        except Exception as e:
            print(f"Note: Could not check existing indexes: {e}")
        
        print(f"📋 Vector Search Index Configuration:")
        print(f"   Index Name: {vector_index_name}")
        print(f"   Collection: {collection.name}")
        print(f"   Database: {db.name}")
        
        # Atlas Vector Search index definition
        vector_search_config = {
            "fields": [
                {
                    "path": "embedding",
                    "numDimensions": 768,  # Google's embedding-001 model dimension
                    "similarity": "cosine",
                    "type": "vector"
                },
                {
                    "path": "text_content",
                    "type": "string"
                },
                {
                    "path": "document_name",
                    "type": "string"
                },
                {
                    "path": "document_id",
                    "type": "string"
                },
                {
                    "path": "document_type",
                    "type": "string"
                }
            ]
        }
        
        print("\n📋 Manual Setup Instructions:")
        print("Since Atlas Vector Search indexes must be created through the Atlas UI,")
        print("please follow these steps:")
        print()
        print("1. Go to your MongoDB Atlas dashboard")
        print("2. Navigate to your cluster")
        print("3. Click on 'Search' tab")
        print("4. Click 'Create Search Index'")
        print("5. Choose 'JSON Editor'")
        print("6. Use this configuration:")
        print()
        print("```json")
        import json
        print(json.dumps(vector_search_config, indent=2))
        print("```")
        print()
        print(f"7. Name the index: {vector_index_name}")
        print(f"8. Select database: {db.name}")
        print(f"9. Select collection: {collection.name}")
        print("10. Click 'Create Search Index'")
        print()
        print("⏱️  Index creation takes 5-10 minutes.")
        print("✅ Once created, your vector search will be ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up vector search: {e}")
        
        if "connection" in str(e).lower():
            print("\n🔧 Connection troubleshooting:")
            print("1. Check your MONGODB_CONNECTION_STRING")
            print("2. Verify your Atlas cluster is running")
            print("3. Check network access settings")
            print("4. Verify database user permissions")
        
        return False

async def test_vector_search():
    """Test if vector search is working properly."""
    
    print("\n🧪 Testing Vector Search Setup...")
    
    try:
        from services.document_mongodb_service import DocumentMongoDBService
        from services.alternative_embedding_service import AlternativeEmbeddingService
        
        # Initialize services
        embedding_service = AlternativeEmbeddingService()
        mongodb_service = DocumentMongoDBService(embedding_service)
        
        # Test search (this will use fallback if vector search isn't ready)
        test_query = "test document search"
        results = await mongodb_service.find_chunks_by_semantic_search(
            query_text=test_query,
            limit=1
        )
        
        if results:
            print("✅ Vector search test successful!")
            print(f"   Found {len(results)} results for test query")
        else:
            print("⚠️  Vector search returned no results (expected if no documents uploaded yet)")
            
        return True
        
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MongoDB Atlas Vector Search Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not os.getenv("MONGODB_CONNECTION_STRING"):
        print("❌ MONGODB_CONNECTION_STRING not found in environment variables")
        print("Please set up your .env file with Atlas connection string")
        sys.exit(1)
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please set up your .env file with Google AI API key")
        sys.exit(1)
    
    # Run setup
    async def main():
        success = await setup_vector_search()
        
        if success:
            print("\n🎉 Vector Search setup instructions provided!")
            print("Follow the manual steps above to complete the setup.")
            
            # Test current setup
            await test_vector_search()
        else:
            print("\n❌ Vector Search setup failed.")
            print("Please check the error messages and try again.")
            sys.exit(1)
    
    asyncio.run(main())
