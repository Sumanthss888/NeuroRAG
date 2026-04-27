"""
Configuration management for NeuroRAG system
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration for NeuroRAG"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    INDEX_DIR = DATA_DIR / "index"
    EXTRACTED_DIR = DATA_DIR / "extracted"
    CHUNKS_DIR = DATA_DIR / "chunks"
    VECTOR_STORE_DIR = BASE_DIR / "vector_store"
    
    # PDF configuration
    PDF_NAME = "19-Neurological-Disorders-2nd-Edition.pdf"
    PDF_PATH = RAW_DATA_DIR / PDF_NAME
    TOC_MASTER_PATH = INDEX_DIR / "toc_master.json"
    CHAPTER_METADATA_PATH = INDEX_DIR / "chapter_metadata.json"
    
    # PDF processing
    PDF_OFFSET = 2  # Offset between TOC pages and actual PDF pages (TOC page 25 = PDF page 27)
    TOTAL_CHAPTERS = 51  # Based on TOC (chapters 1-51)
    
    # Chunking configuration
    CHUNK_SIZE = 300  # tokens
    CHUNK_MIN = 250
    CHUNK_MAX = 400
    CHUNK_OVERLAP = 50  # tokens
    
    # Gemini API configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_EMBEDDING_MODEL = "gemini-embedding-2"
    GEMINI_GENERATION_MODEL = "gemini-2.5-flash"
    EMBEDDING_DIMENSION = 3072
    
    # FAISS configuration
    FAISS_INDEX_TYPE = "Flat"
    TOP_K_CHUNKS = 5
    
    # Mode configuration
    MODES = {
        "clinician": {
            "name": "Clinician Mode",
            "description": "Technical medical terminology and detailed explanations",
            "prompt_suffix": "Provide a technical, detailed response suitable for medical professionals."
        },
        "patient": {
            "name": "Patient Mode",
            "description": "Simplified language with analogies",
            "prompt_suffix": "Provide a simple, easy-to-understand explanation for patients using everyday language and analogies."
        }
    }
    
    # Flask configuration
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5000
    FLASK_DEBUG = True
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = BASE_DIR / "neurorag.log"
    
    # Query matching
    KEYWORD_MATCH_THRESHOLD = 0.3
    MAX_MATCHED_CHAPTERS = 3
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.INDEX_DIR,
            cls.EXTRACTED_DIR,
            cls.CHUNKS_DIR,
            cls.VECTOR_STORE_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        return True