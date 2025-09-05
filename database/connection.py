import asyncio
import os
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Type
from beanie import Document
import certifi

# Global variables to store the client and database
_client: AsyncIOMotorClient = None
_database = None

async def connect_db(document_models: List[Type[Document]]):
    """
    Connects to MongoDB (local or Atlas) using Beanie and initializes document models.
    Enhanced for cloud deployment with better connection handling.
    """
    global _client, _database
    
    mongo_uri = os.getenv("MONGODB_CONNECTION_STRING")
    if not mongo_uri:
        raise ValueError("MONGODB_CONNECTION_STRING environment variable not set.")
    
    mongo_db = os.getenv("DATABASE_NAME", "document_analysis")
    if not mongo_db:
        raise ValueError("DATABASE_NAME environment variable not set.")
    
    # Check if this is an Atlas connection
    is_atlas = "mongodb+srv://" in mongo_uri
    environment = os.getenv("ENVIRONMENT", "development")
    
    db_type = "Atlas Cloud" if is_atlas else "Local"
    print(f"Connecting to MongoDB ({db_type}) in {environment} mode...")
    
    try:
        # Configure client options for cloud hosting
        client_options = {
            "serverSelectionTimeoutMS": 30000,  # 30 second timeout
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000,
            "maxPoolSize": 10,  # Connection pooling
            "minPoolSize": 1,
            "maxIdleTimeMS": 30000,
            "retryWrites": True,
            "retryReads": True,
        }
        
        # Add SSL configuration for Atlas (with Streamlit Cloud compatibility)
        if is_atlas:
            # Try different SSL configurations for cloud environments
            try:
                import ssl
                client_options["tls"] = True
                client_options["tlsCAFile"] = certifi.where()
                
                # For cloud environments like Streamlit Cloud
                if environment == "production":
                    # More permissive SSL for cloud deployment issues
                    client_options["tlsInsecure"] = True
                else:
                    # Strict SSL for development
                    client_options["tlsAllowInvalidCertificates"] = False
                    client_options["tlsAllowInvalidHostnames"] = False
                    
            except Exception as ssl_error:
                print(f"SSL configuration warning: {ssl_error}")
                # Fallback to basic TLS
                client_options["tls"] = True
        
        # Create MongoDB client with enhanced options
        _client = AsyncIOMotorClient(mongo_uri, **client_options)
        _database = _client[mongo_db]
        
        # Test the connection
        await _client.admin.command('hello')
        
        # Initialize Beanie with the database and document models
        await init_beanie(database=_database, document_models=document_models)
        
        print(f"✅ Successfully connected to MongoDB database: {mongo_db}")
        print(f"✅ Database initialized with {len(document_models)} document models")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        if is_atlas:
            print("📋 Atlas connection troubleshooting:")
            print("   1. Check your connection string format")
            print("   2. Verify username/password are correct")
            print("   3. Ensure your IP is whitelisted in Atlas")
            print("   4. Check if the cluster is running")
        raise

def get_database():
    """
    Returns the current database instance.
    """
    global _database
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _database

def get_client():
    """
    Returns the current client instance.
    """
    global _client
    if _client is None:
        raise RuntimeError("Client not initialized. Call connect_db() first.")
    return _client