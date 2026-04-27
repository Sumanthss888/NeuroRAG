"""
Build FAISS vector indices for chapters
"""
import json
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import faiss
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class FAISSBuilder:
    """Build and manage FAISS indices for chapters"""
    
    def __init__(self):
        self.dimension = Config.EMBEDDING_DIMENSION
        self.index_type = Config.FAISS_INDEX_TYPE
    
    def build_chapter_index(self, embeddings: List[List[float]], 
                           chunks: List[Dict],
                           chapter_id: int,
                           chapter_title: str) -> bool:
        """
        Build FAISS index for a single chapter
        
        Args:
            embeddings: List of embedding vectors
            chunks: List of chunk dictionaries
            chapter_id: Chapter ID
            chapter_title: Chapter title
        
        Returns:
            True if successful
        """
        logger.info(f"Building FAISS index for chapter {chapter_id}: {chapter_title}")
        
        try:
            # Filter out None embeddings
            valid_embeddings = []
            valid_chunks = []
            
            for emb, chunk in zip(embeddings, chunks):
                if emb is not None:
                    valid_embeddings.append(emb)
                    valid_chunks.append(chunk)
            
            if not valid_embeddings:
                logger.error(f"No valid embeddings for chapter {chapter_id}")
                return False
            
            # Convert to numpy array
            embeddings_array = np.array(valid_embeddings, dtype=np.float32)
            
            # Create FAISS index (L2 distance)
            if self.index_type == "Flat":
                index = faiss.IndexFlatL2(self.dimension)
            else:
                # Could add other index types here
                index = faiss.IndexFlatL2(self.dimension)
            
            # Add vectors to index
            index.add(embeddings_array)
            
            logger.info(f"Added {embeddings_array.shape[0]} vectors to index")
            
            # Create chapter folder
            chapter_folder = self._get_chapter_folder(chapter_id, chapter_title)
            chapter_folder.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            index_path = chapter_folder / "faiss.index"
            faiss.write_index(index, str(index_path))
            
            # Save metadata
            metadata = {
                "chapter_id": chapter_id,
                "chapter_title": chapter_title,
                "total_vectors": len(valid_embeddings),
                "dimension": self.dimension,
                "chunks": valid_chunks
            }
            
            metadata_path = chapter_folder / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ FAISS index saved to {chapter_folder}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error building FAISS index for chapter {chapter_id}: {e}")
            return False
    
    def load_chapter_index(self, chapter_id: int, 
                          chapter_title: str = None) -> Optional[tuple]:
        """
        Load FAISS index for a chapter
        
        Args:
            chapter_id: Chapter ID
            chapter_title: Chapter title (optional, for folder lookup)
        
        Returns:
            Tuple of (index, metadata) or None if not found
        """
        chapter_folder = self._get_chapter_folder(chapter_id, chapter_title)
        
        index_path = chapter_folder / "faiss.index"
        metadata_path = chapter_folder / "metadata.json"
        
        if not index_path.exists() or not metadata_path.exists():
            logger.warning(f"FAISS index not found for chapter {chapter_id}")
            return None
        
        try:
            # Load index
            index = faiss.read_index(str(index_path))
            
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            logger.info(f"Loaded FAISS index for chapter {chapter_id} "
                       f"({metadata['total_vectors']} vectors)")
            
            return index, metadata
            
        except Exception as e:
            logger.error(f"Error loading FAISS index for chapter {chapter_id}: {e}")
            return None
    
    def _get_chapter_folder(self, chapter_id: int, chapter_title: str = None) -> Path:
        """
        Get chapter folder path
        
        Args:
            chapter_id: Chapter ID
            chapter_title: Chapter title
        
        Returns:
            Path to chapter folder
        """
        if chapter_title:
            # Sanitize title
            import re
            safe_title = re.sub(r'[^a-zA-Z0-9\s]', '', chapter_title)
            safe_title = safe_title.replace(' ', '_').lower()
            folder_name = f"chapter_{chapter_id:02d}_{safe_title}"
        else:
            folder_name = f"chapter_{chapter_id:02d}"
        
        return Config.VECTOR_STORE_DIR / folder_name
    
    def search_similar(self, index: faiss.Index, 
                      query_embedding: List[float],
                      k: int = None) -> tuple:
        """
        Search for similar vectors in index
        
        Args:
            index: FAISS index
            query_embedding: Query embedding vector
            k: Number of results to return
        
        Returns:
            Tuple of (distances, indices)
        """
        k = k or Config.TOP_K_CHUNKS
        
        # Convert to numpy array
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = index.search(query_vector, k)
        
        return distances[0], indices[0]
    
    def build_all_indices(self, embeddings_dict: Dict[int, List[List[float]]],
                         chunks_dict: Dict[int, List[Dict]],
                         toc_data: Dict) -> bool:
        """
        Build FAISS indices for all chapters
        
        Args:
            embeddings_dict: Dictionary mapping chapter_id to embeddings
            chunks_dict: Dictionary mapping chapter_id to chunks
            toc_data: TOC data with chapter information
        
        Returns:
            True if all successful
        """
        logger.info(f"Building FAISS indices for {len(embeddings_dict)} chapters")
        
        success_count = 0
        
        for chapter in toc_data["chapters"]:
            chapter_id = chapter["id"]
            chapter_title = chapter["title"]
            
            if chapter_id in embeddings_dict and chapter_id in chunks_dict:
                embeddings = embeddings_dict[chapter_id]
                chunks = chunks_dict[chapter_id]
                
                success = self.build_chapter_index(
                    embeddings,
                    chunks,
                    chapter_id,
                    chapter_title
                )
                
                if success:
                    success_count += 1
            else:
                logger.warning(f"Missing data for chapter {chapter_id}")
        
        logger.info(f"✓ Built {success_count}/{len(toc_data['chapters'])} FAISS indices")
        
        return success_count == len(toc_data["chapters"])