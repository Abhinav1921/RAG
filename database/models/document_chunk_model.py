# database/models/document_chunk_model.py
from beanie import Document
from typing import List, Optional
from datetime import datetime
import os

class DocumentChunk(Document):
    document_id: str  # Unique identifier for the source document
    document_name: str  # Original filename or document title
    document_type: str  # Type of document (pdf, txt, docx, etc.)
    chunk_index: int  # Order of this chunk within the document
    text_content: str  # The actual text content of this chunk
    embedding: Optional[List[float]] = None  # The vector embedding of text_content
    page_number: Optional[int] = None  # Page number if applicable
    section_title: Optional[str] = None  # Section or heading if available
    char_start: Optional[int] = None  # Start character position in original document
    char_end: Optional[int] = None  # End character position in original document
    timestamp: datetime = datetime.utcnow()  # When this chunk was processed

    class Settings:
        name = os.getenv("COLLECTION_NAME", "document_chunks")  # Collection name
