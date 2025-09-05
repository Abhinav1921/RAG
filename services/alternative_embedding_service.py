# Alternative embedding service using direct Google GenAI client
import google.generativeai as genai
import os
from typing import List
import asyncio
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class AlternativeEmbeddingService:
    def __init__(self):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        
        # Configure the Google GenAI client directly
        genai.configure(api_key=google_api_key)
        
        # Configuration for retry and rate limiting
        self.max_text_length = 8000  # Limit text length to prevent timeouts
        self.rate_limit_delay = 2.0  # Increased delay between requests
        self.last_request_time = 0
        
        print("AlternativeEmbeddingService initialized with direct Google GenAI client")

    async def _rate_limit(self):
        """Implement rate limiting to avoid hitting API limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _truncate_text(self, text: str) -> str:
        """Truncate text to avoid timeouts with large chunks."""
        if len(text) > self.max_text_length:
            print(f"Warning: Text truncated from {len(text)} to {self.max_text_length} characters")
            return text[:self.max_text_length]
        return text
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=20),
        retry=retry_if_exception_type((Exception,))
    )
    async def _get_embedding_with_retry(self, text: str) -> List[float]:
        """Get embedding with retry logic for handling timeouts and errors."""
        try:
            # Use the direct Google GenAI client
            result = await asyncio.to_thread(
                genai.embed_content,
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding (will retry): {e}")
            # Check for specific error types
            if "504" in str(e) or "Deadline Exceeded" in str(e) or "DEADLINE_EXCEEDED" in str(e):
                print("Detected deadline exceeded error - increasing retry delay")
                await asyncio.sleep(5)  # Additional delay for timeout errors
            raise
    
    async def get_embedding(self, text: str) -> List[float]:
        """Generates a vector embedding for the given text with error handling and retries."""
        try:
            # Apply rate limiting
            await self._rate_limit()
            
            # Truncate text if it's too long
            processed_text = self._truncate_text(text)
            
            # Get embedding with retry logic
            return await self._get_embedding_with_retry(processed_text)
            
        except Exception as e:
            error_msg = f"Error generating embedding after retries: {e}"
            print(error_msg)
            
            # Check if it's a 504 timeout error specifically
            if "504" in str(e) or "Deadline Exceeded" in str(e) or "DEADLINE_EXCEEDED" in str(e):
                print("\n🚨 DETECTED 504 DEADLINE EXCEEDED ERROR")
                print("This error typically occurs due to:")
                print("1. Network connectivity issues")
                print("2. Google API server overload")
                print("3. Rate limiting")
                print("4. Very large text chunks")
                print("\nSuggestions to resolve:")
                print("- Wait a few minutes and try again")
                print("- Reduce document chunk size (try 500-800 characters)")
                print("- Check your internet connection")
                print("- Verify your Google API key is valid and has quota")
                print("- Consider using a different embedding model if available")
            
            raise Exception(error_msg)
