"""
Extract text from individual chapters based on page ranges
"""
import json
from typing import Dict, List
from pathlib import Path
import PyPDF2
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ChapterExtractor:
    """Extract text from chapters based on PDF page ranges"""
    
    def __init__(self, pdf_path: Path = None, toc_data: Dict = None):
        self.pdf_path = pdf_path or Config.PDF_PATH
        self.toc_data = toc_data
    
    def extract_all_chapters(self, toc_data: Dict = None) -> Dict[int, str]:
        """
        Extract text from all chapters
        
        Args:
            toc_data: TOC dictionary with page mappings
        
        Returns:
            Dictionary mapping chapter_id to extracted text
        """
        if toc_data:
            self.toc_data = toc_data
        
        if not self.toc_data:
            raise ValueError("TOC data is required")
        
        logger.info("Extracting text from all chapters...")
        
        extracted_chapters = {}
        
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for chapter in self.toc_data["chapters"]:
                    chapter_id = chapter["id"]
                    chapter_text = self.extract_chapter(
                        pdf_reader,
                        chapter["pdf_page_start"],
                        chapter["pdf_page_end"],
                        chapter["title"]
                    )
                    
                    extracted_chapters[chapter_id] = chapter_text
                    
                    # Save individual chapter text file
                    self.save_chapter_text(chapter, chapter_text)
                    
                    logger.info(f"Extracted chapter {chapter_id}: {chapter['title']} "
                              f"({len(chapter_text)} characters)")
        
        except Exception as e:
            logger.error(f"Error extracting chapters: {e}")
            raise
        
        logger.info(f"Extracted {len(extracted_chapters)} chapters")
        return extracted_chapters
    
    def extract_chapter(self, pdf_reader: PyPDF2.PdfReader, 
                       start_page: int, end_page: int, 
                       chapter_title: str) -> str:
        """
        Extract text from a specific chapter
        
        Args:
            pdf_reader: PyPDF2 reader object
            start_page: Starting PDF page (1-indexed)
            end_page: Ending PDF page (1-indexed)
            chapter_title: Chapter title for logging
        
        Returns:
            Extracted text
        """
        text_parts = []
        
        # Convert to 0-indexed
        start_idx = start_page - 1
        end_idx = end_page
        
        for page_num in range(start_idx, end_idx):
            try:
                if page_num < len(pdf_reader.pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        # Clean text
                        text = self.clean_text(text)
                        text_parts.append(text)
            
            except Exception as e:
                logger.warning(f"Error extracting page {page_num + 1}: {e}")
                continue
        
        chapter_text = "\n\n".join(text_parts)
        return chapter_text
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw extracted text
        
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        import re
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove page numbers and headers/footers (basic cleaning)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip very short lines (likely headers/footers)
            if len(line) < 5:
                continue
            
            # Skip lines that are just numbers (page numbers)
            if line.isdigit():
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def save_chapter_text(self, chapter: Dict, text: str):
        """
        Save chapter text to file
        
        Args:
            chapter: Chapter metadata dictionary
            text: Extracted text
        """
        # Create safe filename
        import re
        safe_title = re.sub(r'[^a-zA-Z0-9\s]', '', chapter["title"])
        safe_title = safe_title.replace(' ', '_').lower()
        
        filename = f"chapter_{chapter['id']:02d}_{safe_title}.txt"
        filepath = Config.EXTRACTED_DIR / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.debug(f"Saved chapter text to {filepath}")
    
    def load_chapter_text(self, chapter_id: int) -> str:
        """
        Load chapter text from file
        
        Args:
            chapter_id: Chapter ID
        
        Returns:
            Chapter text
        """
        # Find the chapter in TOC
        chapter = next((ch for ch in self.toc_data["chapters"] if ch["id"] == chapter_id), None)
        
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found in TOC")
        
        # Build filename
        import re
        safe_title = re.sub(r'[^a-zA-Z0-9\s]', '', chapter["title"])
        safe_title = safe_title.replace(' ', '_').lower()
        
        filename = f"chapter_{chapter_id:02d}_{safe_title}.txt"
        filepath = Config.EXTRACTED_DIR / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Chapter text not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()