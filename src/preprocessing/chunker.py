"""
Intelligent text chunking for RAG
"""
import json
import re
from typing import List, Dict
from pathlib import Path
import tiktoken
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class Chunker:
    """Intelligent text chunking with context preservation"""
    
    def __init__(self):
        # Use tiktoken for accurate token counting
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except:
            self.encoding = None
            logger.warning("tiktoken not available, using approximate token counting")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        
        Args:
            text: Input text
        
        Returns:
            Token count
        """
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Approximate: 1 token ≈ 4 characters
            return len(text) // 4
    
    def chunk_text(self, text: str, chapter_id: int, chapter_title: str) -> List[Dict]:
        """
        Chunk text intelligently while preserving context
        
        Args:
            text: Chapter text
            chapter_id: Chapter ID
            chapter_title: Chapter title
        
        Returns:
            List of chunk dictionaries
        """
        logger.info(f"Chunking chapter {chapter_id}: {chapter_title}")
        
        chunks = []
        
        # Split by paragraphs first
        paragraphs = self._split_into_paragraphs(text)
        
        current_chunk = []
        current_tokens = 0
        chunk_id = 1
        
        for para in paragraphs:
            para_tokens = self.count_tokens(para)
            
            # If single paragraph exceeds max, split it further
            if para_tokens > Config.CHUNK_MAX:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk, 
                        chapter_id, 
                        chapter_title, 
                        chunk_id
                    ))
                    chunk_id += 1
                    current_chunk = []
                    current_tokens = 0
                
                # Split large paragraph by sentences
                sub_chunks = self._split_large_paragraph(para, chapter_id, chapter_title, chunk_id)
                chunks.extend(sub_chunks)
                chunk_id += len(sub_chunks)
            
            # If adding this paragraph exceeds max, save current chunk
            elif current_tokens + para_tokens > Config.CHUNK_MAX:
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk, 
                        chapter_id, 
                        chapter_title, 
                        chunk_id
                    ))
                    chunk_id += 1
                
                # Start new chunk with overlap
                if len(current_chunk) > 0:
                    # Add last paragraph as overlap
                    current_chunk = [current_chunk[-1], para]
                    current_tokens = self.count_tokens(current_chunk[-1]) + para_tokens
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            
            # If within range, add to current chunk
            elif current_tokens + para_tokens >= Config.CHUNK_MIN:
                current_chunk.append(para)
                current_tokens += para_tokens
                
                # Save chunk if we're at a good stopping point
                chunks.append(self._create_chunk(
                    current_chunk, 
                    chapter_id, 
                    chapter_title, 
                    chunk_id
                ))
                chunk_id += 1
                
                # Start new chunk with overlap
                current_chunk = [para]
                current_tokens = para_tokens
            
            else:
                # Add to current chunk
                current_chunk.append(para)
                current_tokens += para_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                current_chunk, 
                chapter_id, 
                chapter_title, 
                chunk_id
            ))
        
        logger.info(f"Created {len(chunks)} chunks for chapter {chapter_id}")
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newline or more
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Filter out empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _split_large_paragraph(self, paragraph: str, chapter_id: int, 
                               chapter_title: str, start_chunk_id: int) -> List[Dict]:
        """Split a large paragraph by sentences"""
        # Split by sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        chunks = []
        current_sentences = []
        current_tokens = 0
        chunk_id = start_chunk_id
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            if current_tokens + sentence_tokens > Config.CHUNK_MAX:
                if current_sentences:
                    chunks.append(self._create_chunk(
                        [' '.join(current_sentences)], 
                        chapter_id, 
                        chapter_title, 
                        chunk_id
                    ))
                    chunk_id += 1
                
                current_sentences = [sentence]
                current_tokens = sentence_tokens
            else:
                current_sentences.append(sentence)
                current_tokens += sentence_tokens
        
        # Add remaining sentences
        if current_sentences:
            chunks.append(self._create_chunk(
                [' '.join(current_sentences)], 
                chapter_id, 
                chapter_title, 
                chunk_id
            ))
        
        return chunks
    
    def _create_chunk(self, paragraphs: List[str], chapter_id: int, 
                     chapter_title: str, chunk_id: int) -> Dict:
        """Create a chunk dictionary"""
        text = '\n\n'.join(paragraphs)
        token_count = self.count_tokens(text)
        
        chunk = {
            "chunk_id": f"{chapter_id:02d}_{chunk_id:03d}",
            "text": text,
            "token_count": token_count,
            "chapter_id": chapter_id,
            "chapter_title": chapter_title
        }
        
        return chunk
    
    def save_chunks(self, chunks: List[Dict], chapter_id: int):
        """
        Save chunks to JSON file
        
        Args:
            chunks: List of chunk dictionaries
            chapter_id: Chapter ID
        """
        # Create chunks file structure
        chunks_data = {
            "chapter_id": chapter_id,
            "chapter_title": chunks[0]["chapter_title"] if chunks else "",
            "total_chunks": len(chunks),
            "chunks": chunks
        }
        
        # Save to file
        filename = f"chapter_{chapter_id:02d}_chunks.json"
        filepath = Config.CHUNKS_DIR / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(chunks)} chunks to {filepath}")
    
    def load_chunks(self, chapter_id: int) -> List[Dict]:
        """
        Load chunks from JSON file
        
        Args:
            chapter_id: Chapter ID
        
        Returns:
            List of chunk dictionaries
        """
        filename = f"chapter_{chapter_id:02d}_chunks.json"
        filepath = Config.CHUNKS_DIR / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Chunks file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data["chunks"]