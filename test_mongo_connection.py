#!/usr/bin/env python3
"""
Test MongoDB Atlas connection - Use this to verify your connection string works
"""

import os
import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mongodb_connection():
    """Test MongoDB Atlas connection with detailed error reporting"""
    
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    
    if not connection_string:
        print("❌ Error: MONGODB_CONNECTION_STRING not found in environment variables")
        print("Please check your .env file or environment variables")
        return False
    
    # Mask password in connection string for logging
    masked_string = connection_string
    if "@" in masked_string and "://" in masked_string:
        parts = masked_string.split("://")
        if len(parts) > 1 and "@" in parts[1]:
            auth_part = parts[1].split("@")[0]
            if ":" in auth_part:
                username, password = auth_part.split(":", 1)
                masked_string = connection_string.replace(password, "***")
    
    print(f"🔗 Testing connection to: {masked_string}")
    
    try:
        # Test with pymongo first (simpler)
        print("\n📦 Testing with pymongo...")
        
        from pymongo import MongoClient
        from pymongo.server_api import ServerApi
        
        # Create client with explicit timeout settings
        client = MongoClient(
            connection_string,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=10000,  # 10 seconds
            connectTimeoutMS=10000,  # 10 seconds
            socketTimeoutMS=10000,   # 10 seconds
            maxPoolSize=10,
            retryWrites=True
        )
        
        # Test the connection
        print("🔍 Testing server connection...")
        client.admin.command('ping')
        print("✅ Ping successful!")
        
        # Test database access
        db_name = os.getenv("DATABASE_NAME", "document_analysis")
        collection_name = os.getenv("COLLECTION_NAME", "document_chunks")
        
        print(f"🗄️  Testing database access: {db_name}.{collection_name}")
        db = client[db_name]
        collection = db[collection_name]
        
        # Try to get collection stats (this tests read permissions)
        stats = db.command("collstats", collection_name)
        print(f"✅ Collection access successful! Documents: {stats.get('count', 'unknown')}")
        
        client.close()
        print("✅ MongoDB connection test PASSED!")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ MongoDB connection test FAILED: {error_msg}")
        
        # Provide specific troubleshooting advice
        if "timeout" in error_msg.lower():
            print("\n🔧 TIMEOUT ISSUE DETECTED:")
            print("1. Check MongoDB Atlas Network Access:")
            print("   - Go to Atlas → Network Access")
            print("   - Ensure 0.0.0.0/0 is allowed")
            print("   - Wait 2-3 minutes after adding the IP")
            print("\n2. Check cluster status:")
            print("   - Ensure cluster is not paused")
            print("   - Verify cluster is running")
            
        elif "authentication" in error_msg.lower() or "auth" in error_msg.lower():
            print("\n🔧 AUTHENTICATION ISSUE DETECTED:")
            print("1. Verify username and password in connection string")
            print("2. Check Database Access in Atlas:")
            print("   - Go to Atlas → Database Access")
            print("   - Verify user exists and has proper permissions")
            print("   - Ensure password is correct")
            
        elif "ssl" in error_msg.lower() or "tls" in error_msg.lower():
            print("\n🔧 SSL/TLS ISSUE DETECTED:")
            print("1. Try updating certifi: pip install --upgrade certifi")
            print("2. Check if your system clock is correct")
            print("3. This might be a temporary issue - try again in a few minutes")
            
        else:
            print(f"\n🔧 GENERAL TROUBLESHOOTING:")
            print("1. Verify connection string format:")
            print("   Should start with: mongodb+srv://")
            print("2. Check for special characters in password (URL encode them)")
            print("3. Verify cluster name and region")
            
        return False

async def test_beanie_connection():
    """Test Beanie/Motor connection (used by the application)"""
    
    print("\n📦 Testing with Beanie/Motor (application method)...")
    
    try:
        # Import the application's connection method
        sys.path.append(os.path.dirname(__file__))
        
        try:
            from database.cloud_connection import connect_db_cloud_safe as connect_db
            print("Using cloud_connection module")
        except ImportError:
            from database.connection import connect_db
            print("Using standard connection module")
        
        from database.models.document_chunk_model import DocumentChunk
        
        # Test the connection
        await connect_db(document_models=[DocumentChunk])
        print("✅ Beanie connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Beanie connection test FAILED: {str(e)}")
        return False

def check_environment_variables():
    """Check if all required environment variables are set"""
    
    print("🔍 Checking environment variables...")
    
    required_vars = [
        "MONGODB_CONNECTION_STRING",
        "GOOGLE_API_KEY",
        "DATABASE_NAME",
        "COLLECTION_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == "MONGODB_CONNECTION_STRING":
                masked = value[:20] + "***" + value[-10:] if len(value) > 30 else "***"
                print(f"✅ {var}: {masked}")
            elif var == "GOOGLE_API_KEY":
                masked = value[:8] + "***" + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All environment variables are set!")
        return True

async def main():
    """Run all connection tests"""
    
    print("🚀 MongoDB Atlas Connection Test")
    print("=" * 50)
    
    # Check environment variables first
    env_ok = check_environment_variables()
    if not env_ok:
        print("\n❌ Please set missing environment variables and try again")
        return
    
    print("\n" + "=" * 50)
    
    # Test basic MongoDB connection
    mongo_ok = await test_mongodb_connection()
    
    print("\n" + "=" * 50)
    
    # Test application-specific connection
    beanie_ok = await test_beanie_connection()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"MongoDB Connection: {'✅ PASS' if mongo_ok else '❌ FAIL'}")
    print(f"Beanie Connection: {'✅ PASS' if beanie_ok else '❌ FAIL'}")
    
    if all([env_ok, mongo_ok, beanie_ok]):
        print("\n🎉 ALL TESTS PASSED! Your MongoDB connection is working correctly.")
        print("You should be able to deploy to Render successfully.")
    else:
        print("\n❌ Some tests failed. Please fix the issues above before deploying.")

if __name__ == "__main__":
    asyncio.run(main())
