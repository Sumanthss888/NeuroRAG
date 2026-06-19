"""
Retrieve relevant chunks from FAISS indices
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
from ..embeddings.faiss_builder import FAISSBuilder
from ..embeddings.gemini_embedder import GeminiEmbedder
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ChunkRetriever:
    """Retrieve relevant chunks from chapter indices"""
    
    def __init__(self, embedder: GeminiEmbedder = None):
        self.faiss_builder = FAISSBuilder()
        self.embedder = embedder or GeminiEmbedder()
    
    def retrieve_from_chapters(self, query: str, 
                              matched_chapters: List[Dict],
                              top_k: int = None) -> List[Dict]:
        """
        Retrieve relevant chunks from matched chapters
        
        Args:
            query: User query
            matched_chapters: List of matched chapter dictionaries with scores
            top_k: Number of chunks to retrieve per chapter
        
        Returns:
            List of retrieved chunks with metadata
        """
        top_k = top_k or Config.TOP_K_CHUNKS
        
        logger.info(f"Retrieving chunks from {len(matched_chapters)} chapters")
        
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []
        
        all_chunks = []
        
        for match in matched_chapters:
            chapter = match["chapter"]
            chapter_id = chapter["id"]
            chapter_title = chapter["title"]
            chapter_score = match["score"]
            
            # Load chapter index
            index_data = self.faiss_builder.load_chapter_index(chapter_id, chapter_title)
            
            if not index_data:
                logger.warning(f"Could not load index for chapter {chapter_id}")
                continue
            
            index, metadata = index_data
            
            # Search in index
            distances, indices = self.faiss_builder.search_similar(
                index,
                query_embedding,
                k=top_k
            )
            
            # Get chunks
            chunks_metadata = metadata["chunks"]
            
            for i, (distance, idx) in enumerate(zip(distances, indices)):
                if idx < len(chunks_metadata):
                    chunk = chunks_metadata[idx].copy()
                    
                    # Add retrieval metadata (convert numpy types to Python types)
                    chunk["distance"] = float(distance)
                    chunk["similarity"] = self._distance_to_similarity(float(distance))
                    chunk["chapter_match_score"] = float(chapter_score)
                    chunk["rank"] = int(i + 1)
                    chunk["source_chapter_id"] = int(chapter_id)
                    chunk["source_chapter_title"] = chapter_title
                    
                    all_chunks.append(chunk)
        
        # Sort by combined score (similarity + chapter match score)
        all_chunks.sort(
            key=lambda x: (x["similarity"] * 0.7 + x["chapter_match_score"] * 0.3),
            reverse=True
        )
        
        # Take top K overall
        final_chunks = all_chunks[:top_k]
        
        logger.info(f"Retrieved {len(final_chunks)} chunks")
        
        return final_chunks
    
    def _distance_to_similarity(self, distance: float) -> float:
        """
        Convert L2 distance to similarity score (0-1)
        
        Args:
            distance: L2 distance
        
        Returns:
            Similarity score (closer to 1 is more similar)
        """
        # Use exponential decay: similarity = e^(-distance)
        # Convert to Python float to avoid JSON serialization issues
        return float(np.exp(-distance / 100.0))
    
    def format_context_for_rag(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks as context for RAG
        
        Args:
            chunks: List of retrieved chunks
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            chapter_title = chunk.get("source_chapter_title", "Unknown Chapter")
            chunk_text = chunk.get("text", "")
            
            context_parts.append(
                f"[Source {i}: Chapter - {chapter_title}]\n{chunk_text}"
            )
        
        context = "\n\n".join(context_parts)
        
        return context
    
    def get_citations(self, chunks: List[Dict]) -> List[Dict]:
        """
        Extract citations from retrieved chunks
        
        Args:
            chunks: List of retrieved chunks
        
        Returns:
            List of citation dictionaries
        """
        import json
        import os
        
        toc_map = {}
        try:
            if os.path.exists(Config.TOC_MASTER_PATH):
                with open(Config.TOC_MASTER_PATH, 'r') as f:
                    toc_data = json.load(f)
                    for ch in toc_data.get("chapters", []):
                        toc_map[int(ch["id"])] = {
                            "page_start": ch.get("pdf_page_start"),
                            "page_end": ch.get("pdf_page_end")
                        }
        except Exception as e:
            logger.error(f"Error loading toc_master.json: {e}")

        citations = []
        seen_chapters = set()
        
        for chunk in chunks:
            chapter_id = chunk.get("source_chapter_id")
            if chapter_id is None:
                continue
            chapter_id = int(chapter_id)
            chapter_title = chunk.get("source_chapter_title", "Unknown")
            
            if chapter_id not in seen_chapters:
                # Find all chunks text for this chapter_id
                chapter_chunks = [ch.get("text", "") for ch in chunks if int(ch.get("source_chapter_id", -1)) == chapter_id and ch.get("text")]
                
                # Fetch page range
                page_start = ""
                page_end = ""
                if chapter_id in toc_map:
                    page_start = toc_map[chapter_id].get("page_start", "")
                    page_end = toc_map[chapter_id].get("page_end", "")
                
                page_range = f"{page_start}-{page_end}" if page_start and page_end else ""
                
                citations.append({
                    "chapter_id": chapter_id,
                    "chapter_title": str(chapter_title),
                    "similarity": float(chunk.get("similarity", 0.0)),
                    "source_name": str(chapter_title),
                    "page_range": page_range,
                    "retrieved_chunks": chapter_chunks
                })
                seen_chapters.add(chapter_id)
        
        return citations