"""
Generate embeddings using Google Gemini API
"""
from typing import List, Optional
import time
from google import genai
from google.genai import types
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class GeminiEmbedder:
    """Generate embeddings using Gemini text-embedding-004"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model = Config.GEMINI_EMBEDDING_MODEL
        
        logger.info(f"Initialized Gemini Embedder with model: {self.model}")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector (768 dimensions)
        """
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text
            )
            
            if result and result.embeddings:
                embedding = result.embeddings[0].values
                return embedding
            
            logger.warning("No embedding returned from Gemini")
            return None
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str], 
                                  batch_size: int = 20) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once
        
        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(texts)} texts in batches of {batch_size}")
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            
            for text in batch:
                embedding = self.generate_embedding(text)
                batch_embeddings.append(embedding)
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
            
            all_embeddings.extend(batch_embeddings)
            
            logger.info(f"Processed batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size}")
        
        logger.info(f"✓ Generated {len([e for e in all_embeddings if e])} embeddings successfully")
        
        return all_embeddings
    
    def embed_query(self, query: str) -> Optional[List[float]]:
        """
        Generate embedding for user query
        
        Args:
            query: User query text
        
        Returns:
            Query embedding vector
        """
        logger.info(f"Generating query embedding: {query[:50]}...")
        
        embedding = self.generate_embedding(query)
        
        if embedding:
            logger.info("Query embedding generated successfully")
        else:
            logger.warning("Failed to generate query embedding")
        
        return embedding