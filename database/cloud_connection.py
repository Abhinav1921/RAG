"""
Alternative MongoDB connection specifically for cloud deployment issues.
This handles SSL/TLS problems common in Streamlit Cloud and other platforms.
"""

import asyncio
import os
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Type
from beanie import Document
import ssl
import urllib.parse

# Global variables to store the client and database
_client: AsyncIOMotorClient = None
_database = None

async def connect_db_cloud_safe(document_models: List[Type[Document]]):
    """
    Cloud-safe MongoDB connection with multiple fallback strategies.
    Specifically designed for Streamlit Cloud deployment.
    """
    global _client, _database
    
    mongo_uri = os.getenv("MONGODB_CONNECTION_STRING")
    if not mongo_uri:
        raise ValueError("MONGODB_CONNECTION_STRING environment variable not set.")
    
    mongo_db = os.getenv("DATABASE_NAME", "document_analysis")
    environment = os.getenv("ENVIRONMENT", "development")
    
    print(f"🔧 Attempting cloud-safe MongoDB connection...")
    print(f"Environment: {environment}")
    
    # Multiple connection strategies to try
    connection_strategies = [
        ("Standard SSL", get_standard_ssl_options),
        ("Relaxed SSL", get_relaxed_ssl_options),
        ("Minimal SSL", get_minimal_ssl_options),
        ("Basic Connection", get_basic_options)
    ]
    
    last_error = None
    
    for strategy_name, option_func in connection_strategies:
        print(f"🔄 Trying {strategy_name} connection...")
        
        try:
            client_options = option_func()
            _client = AsyncIOMotorClient(mongo_uri, **client_options)
            _database = _client[mongo_db]
            
            # Test the connection with a short timeout
            await asyncio.wait_for(_client.admin.command('hello'), timeout=15.0)
            
            # Initialize Beanie
            await init_beanie(database=_database, document_models=document_models)
            
            print(f"✅ Successfully connected using {strategy_name}")
            print(f"✅ Database: {mongo_db}")
            print(f"✅ Models initialized: {len(document_models)}")
            
            return True
            
        except asyncio.TimeoutError:
            print(f"❌ {strategy_name}: Connection timeout")
            last_error = f"{strategy_name}: Connection timeout"
            
        except Exception as e:
            print(f"❌ {strategy_name}: {str(e)[:100]}...")
            last_error = f"{strategy_name}: {str(e)}"
            
        # Clean up failed connection
        if _client:
            _client.close()
            _client = None
            _database = None
            
        # Wait a bit before trying next strategy
        await asyncio.sleep(1)
    
    # All strategies failed
    print(f"\n❌ All connection strategies failed!")
    print(f"Last error: {last_error}")
    print("\n🔧 Troubleshooting suggestions:")
    print("1. Check MongoDB Atlas cluster is running")
    print("2. Verify network access allows 0.0.0.0/0")
    print("3. Check connection string format")
    print("4. Try restarting the Streamlit app")
    
    raise Exception(f"Could not connect to MongoDB Atlas. Last error: {last_error}")

def get_standard_ssl_options():
    """Standard SSL configuration - most secure."""
    return {
        "serverSelectionTimeoutMS": 15000,
        "connectTimeoutMS": 15000,
        "socketTimeoutMS": 15000,
        "maxPoolSize": 5,
        "minPoolSize": 1,
        "maxIdleTimeMS": 15000,
        "retryWrites": True,
        "retryReads": True,
    }

def get_relaxed_ssl_options():
    """Relaxed SSL configuration for cloud environments."""
    try:
        import certifi
        return {
            "serverSelectionTimeoutMS": 20000,
            "connectTimeoutMS": 20000,
            "socketTimeoutMS": 20000,
            "maxPoolSize": 3,
            "minPoolSize": 1,
            "retryWrites": True,
            "retryReads": True,
            "tls": True,
            "tlsCAFile": certifi.where(),
            "tlsInsecure": True,  # Allow insecure connections for cloud compatibility
        }
    except ImportError:
        return get_minimal_ssl_options()

def get_minimal_ssl_options():
    """Minimal SSL configuration."""
    return {
        "serverSelectionTimeoutMS": 25000,
        "connectTimeoutMS": 25000,
        "socketTimeoutMS": 25000,
        "maxPoolSize": 2,
        "minPoolSize": 1,
        "retryWrites": True,
        "tls": True,
    }

def get_basic_options():
    """Most basic connection options."""
    return {
        "serverSelectionTimeoutMS": 30000,
        "connectTimeoutMS": 30000,
        "socketTimeoutMS": 30000,
        "maxPoolSize": 1,
        "retryWrites": True,
    }

def get_database():
    """Returns the current database instance."""
    global _database
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_db_cloud_safe() first.")
    return _database

def get_client():
    """Returns the current client instance."""
    global _client
    if _client is None:
        raise RuntimeError("Client not initialized. Call connect_db_cloud_safe() first.")
    return _client
