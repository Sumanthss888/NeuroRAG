"""
Complete preprocessing pipeline for NeuroRAG
Run this script to:
1. Extract TOC from PDF
2. Map pages
3. Extract chapters
4. Chunk text
5. Generate embeddings
6. Build FAISS indices
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.preprocessing.toc_extractor import TOCExtractor
from src.preprocessing.page_mapper import PageMapper
from src.preprocessing.chapter_extractor import ChapterExtractor
from src.preprocessing.chunker import Chunker
from src.embeddings.gemini_embedder import GeminiEmbedder
from src.embeddings.faiss_builder import FAISSBuilder
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PreprocessingPipeline:
    """Complete preprocessing pipeline"""
    
    def __init__(self):
        # Create directories
        Config.create_directories()
        
        # Initialize components
        self.toc_extractor = TOCExtractor()
        self.page_mapper = PageMapper()
        self.chapter_extractor = ChapterExtractor()
        self.chunker = Chunker()
        self.embedder = GeminiEmbedder()
        self.faiss_builder = FAISSBuilder()
        
        self.toc_data = None
    
    def run_full_pipeline(self):
        """Run the complete preprocessing pipeline"""
        logger.info("=" * 60)
        logger.info("NEURORAG PREPROCESSING PIPELINE")
        logger.info("=" * 60)
        
        try:
            # Step 1: Extract TOC
            logger.info("\n[STEP 1/6] Extracting Table of Contents...")
            self.extract_toc()
            
            # Step 2: Map pages
            logger.info("\n[STEP 2/6] Mapping TOC pages to actual PDF pages...")
            self.map_pages()
            
            # Step 3: Extract chapters
            logger.info("\n[STEP 3/6] Extracting text from chapters...")
            self.extract_chapters()
            
            # Step 4: Chunk text
            logger.info("\n[STEP 4/6] Chunking text...")
            chunks_dict = self.chunk_chapters()
            
            # Step 5: Generate embeddings
            logger.info("\n[STEP 5/6] Generating embeddings...")
            embeddings_dict = self.generate_embeddings(chunks_dict)
            
            # Step 6: Build FAISS indices
            logger.info("\n[STEP 6/6] Building FAISS indices...")
            self.build_indices(embeddings_dict, chunks_dict)
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ PREPROCESSING COMPLETE!")
            logger.info("=" * 60)
            logger.info("You can now run: python app.py")
            
        except Exception as e:
            logger.error(f"\n✗ PIPELINE FAILED: {e}")
            raise
    
    def extract_toc(self):
        """Step 1: Extract TOC"""
        self.toc_data = self.toc_extractor.extract_toc()
        self.toc_extractor.save_toc()
        logger.info(f"✓ Extracted {len(self.toc_data['chapters'])} chapters")
    
    def map_pages(self):
        """Step 2: Map pages"""
        self.toc_data = self.page_mapper.map_pages(self.toc_data)
        self.page_mapper.validate_page_ranges()
        
        # Save updated TOC
        self.toc_extractor.toc_data = self.toc_data
        self.toc_extractor.save_toc()
        logger.info("✓ Page mapping complete")
    
    def extract_chapters(self):
        """Step 3: Extract chapters"""
        self.chapter_extractor.toc_data = self.toc_data
        extracted = self.chapter_extractor.extract_all_chapters()
        logger.info(f"✓ Extracted {len(extracted)} chapters")
    
    def chunk_chapters(self):
        """Step 4: Chunk text"""
        chunks_dict = {}
        
        for chapter in self.toc_data["chapters"]:
            chapter_id = chapter["id"]
            chapter_title = chapter["title"]
            
            # Load chapter text
            text = self.chapter_extractor.load_chapter_text(chapter_id)
            
            # Chunk it
            chunks = self.chunker.chunk_text(text, chapter_id, chapter_title)
            
            # Save chunks
            self.chunker.save_chunks(chunks, chapter_id)
            
            chunks_dict[chapter_id] = chunks
        
        logger.info(f"✓ Chunked {len(chunks_dict)} chapters")
        return chunks_dict
    
    def generate_embeddings(self, chunks_dict):
        """Step 5: Generate embeddings"""
        embeddings_dict = {}
        
        for chapter_id, chunks in chunks_dict.items():
            logger.info(f"Generating embeddings for chapter {chapter_id}...")
            
            # Extract texts
            texts = [chunk["text"] for chunk in chunks]
            
            # Generate embeddings in batch
            embeddings = self.embedder.generate_embeddings_batch(texts, batch_size=10)
            
            embeddings_dict[chapter_id] = embeddings
        
        logger.info(f"✓ Generated embeddings for {len(embeddings_dict)} chapters")
        return embeddings_dict
    
    def build_indices(self, embeddings_dict, chunks_dict):
        """Step 6: Build FAISS indices"""
        success = self.faiss_builder.build_all_indices(
            embeddings_dict,
            chunks_dict,
            self.toc_data
        )
        
        if success:
            logger.info("✓ Built all FAISS indices")
        else:
            logger.warning("Some indices failed to build")

if __name__ == "__main__":
    try:
        # Validate config
        Config.validate_config()
        
        # Check PDF exists
        if not Config.PDF_PATH.exists():
            logger.error(f"PDF not found: {Config.PDF_PATH}")
            logger.error("Please place your PDF in: data/raw/neurology_handbook.pdf")
            sys.exit(1)
        
        # Run pipeline
        pipeline = PreprocessingPipeline()
        pipeline.run_full_pipeline()
        
    except KeyboardInterrupt:
        logger.info("\n\nPipeline interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)