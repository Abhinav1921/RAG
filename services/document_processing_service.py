# services/document_processing_service.py
import os
import uuid
from typing import List, Dict, Any, Tuple
from pathlib import Path
import asyncio

class DocumentProcessingService:
    def __init__(self):
        self.supported_extensions = {'.txt', '.md', '.pdf', '.docx', '.doc'}
        
    def is_supported_format(self, file_path: str) -> bool:
        """Check if the file format is supported"""
        return Path(file_path).suffix.lower() in self.supported_extensions
    
    async def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file formats"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.txt' or file_extension == '.md':
            return await self._extract_from_txt(file_path)
        elif file_extension == '.pdf':
            return await self._extract_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return await self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    async def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            raise ImportError("PyPDF2 is required for PDF processing. Install with: pip install PyPDF2")
    
    async def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from Word documents"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            raise ImportError("python-docx is required for Word document processing. Install with: pip install python-docx")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = start + chunk_size
            
            # If not the last chunk, try to break at a sentence or paragraph
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                last_period = text.rfind('.', max(start, end - 100), end)
                last_newline = text.rfind('\n', max(start, end - 100), end)
                
                # Use the latest sentence/paragraph break found
                break_point = max(last_period, last_newline)
                if break_point > start:
                    end = break_point + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunks.append({
                    'chunk_index': chunk_index,
                    'text_content': chunk_text,
                    'char_start': start,
                    'char_end': end
                })
                chunk_index += 1
            
            # Move start position (with overlap)
            start = max(start + 1, end - overlap)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    async def process_document(self, file_path: str, chunk_size: int = 1000, overlap: int = 200) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Process a document file and return document info and chunks
        
        Returns:
            Tuple of (document_id, document_name, chunks)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.is_supported_format(file_path):
            raise ValueError(f"Unsupported file format: {Path(file_path).suffix}")
        
        # Generate document ID and extract name
        document_id = str(uuid.uuid4())
        document_name = Path(file_path).name
        document_type = Path(file_path).suffix.lower()[1:]  # Remove the dot
        
        # Extract text from document
        text_content = await self.extract_text_from_file(file_path)
        
        if not text_content.strip():
            raise ValueError("No text content found in the document")
        
        # Create chunks
        chunks = self.chunk_text(text_content, chunk_size, overlap)
        
        # Add document metadata to each chunk
        for chunk in chunks:
            chunk.update({
                'document_id': document_id,
                'document_name': document_name,
                'document_type': document_type
            })
        
        return document_id, document_name, chunks
