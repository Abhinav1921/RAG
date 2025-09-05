#!/usr/bin/env python3
"""
Diagnostic script to check Google API status, quota, and connectivity.
"""

import os
import asyncio
import sys
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

async def diagnose_google_api():
    """Comprehensive diagnosis of Google API issues."""
    
    print("🔍 Google API Diagnostic Report")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        # Configure the client
        genai.configure(api_key=api_key)
        print("✅ Google GenAI client configured")
        
        # Test 1: List models to check API connectivity
        print("\n📋 Available Models:")
        try:
            models = list(genai.list_models())
            embedding_models = [m for m in models if 'embedding' in m.name]
            print(f"   Total models available: {len(models)}")
            print(f"   Embedding models: {len(embedding_models)}")
            for model in embedding_models:
                print(f"     - {model.name}")
        except Exception as e:
            print(f"❌ Failed to list models: {e}")
            return False
        
        # Test 2: Simple embedding test
        print("\n🧪 Testing Embedding API:")
        test_texts = [
            "Hello",
            "This is a test sentence.",
            "This is a longer test sentence that contains more words and should help us understand if the issue is related to text length or not."
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n   Test {i} - Text length: {len(text)} chars")
            try:
                start_time = time.time()
                
                # Test with direct API call
                result = await asyncio.to_thread(
                    genai.embed_content,
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document"
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                embedding = result['embedding']
                print(f"   ✅ Success! Dimension: {len(embedding)}, Time: {duration:.2f}s")
                
                # Add delay to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                
                # Specific error analysis
                error_str = str(e).lower()
                if "504" in error_str or "deadline exceeded" in error_str:
                    print("   🚨 This is the 504 Deadline Exceeded error!")
                    print("   🔍 Possible causes:")
                    print("      - Google API server overload")
                    print("      - Network connectivity issues")
                    print("      - Rate limiting")
                    print("      - Regional API server issues")
                elif "quota" in error_str or "limit" in error_str:
                    print("   🚨 Quota/Rate limit issue detected!")
                elif "authentication" in error_str or "api key" in error_str:
                    print("   🚨 API key authentication issue!")
                elif "permission" in error_str:
                    print("   🚨 Permission issue - check if embedding API is enabled!")
                
                return False
        
        print("\n✅ All embedding tests passed!")
        
        # Test 3: Concurrent request test
        print("\n⚡ Testing Concurrent Requests:")
        try:
            async def single_embed(text, index):
                try:
                    result = await asyncio.to_thread(
                        genai.embed_content,
                        model="models/embedding-001",
                        content=f"Test {index}: {text}",
                        task_type="retrieval_document"
                    )
                    return f"Request {index}: Success"
                except Exception as e:
                    return f"Request {index}: Failed - {e}"
            
            # Create 3 concurrent requests
            tasks = [single_embed("Test text", i) for i in range(1, 4)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                print(f"   {result}")
                
        except Exception as e:
            print(f"   ❌ Concurrent test failed: {e}")
        
        print(f"\n🎉 Diagnostic completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to configure Google GenAI: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Google API Diagnosis...")
    
    success = asyncio.run(diagnose_google_api())
    
    if success:
        print("\n✅ Google API is working correctly!")
        print("If you're still experiencing 504 errors, try:")
        print("1. Use the AlternativeEmbeddingService instead of the original")
        print("2. Reduce document chunk sizes to 500-800 characters")
        print("3. Add longer delays between API calls")
        print("4. Try again during off-peak hours")
    else:
        print("\n❌ Google API issues detected. Please resolve the above issues first.")
        sys.exit(1)
