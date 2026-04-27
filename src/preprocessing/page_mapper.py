"""
Map TOC page numbers to actual PDF page numbers
"""
import json
from typing import Dict, List
from pathlib import Path
import PyPDF2
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class PageMapper:
    """Map TOC page numbers to actual PDF pages"""
    
    def __init__(self, pdf_path: Path = None, toc_data: Dict = None):
        self.pdf_path = pdf_path or Config.PDF_PATH
        self.toc_data = toc_data
    
    def map_pages(self, toc_data: Dict = None) -> Dict:
        """
        Map TOC pages to actual PDF pages by finding chapter boundaries
        
        Args:
            toc_data: TOC dictionary from TOCExtractor
        
        Returns:
            Updated TOC with accurate PDF page ranges
        """
        if toc_data:
            self.toc_data = toc_data
        
        if not self.toc_data:
            raise ValueError("TOC data is required")
        
        logger.info("Mapping TOC pages to actual PDF pages...")
        
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                logger.info(f"PDF has {total_pages} pages")
                
                chapters = self.toc_data["chapters"]
                
                # Update end pages based on next chapter's start
                for i in range(len(chapters)):
                    current_chapter = chapters[i]
                    
                    # Set end page based on next chapter or PDF end
                    if i < len(chapters) - 1:
                        next_chapter = chapters[i + 1]
                        current_chapter["pdf_page_end"] = next_chapter["pdf_page_start"] - 1
                    else:
                        # Last chapter goes to end of PDF
                        current_chapter["pdf_page_end"] = total_pages
                    
                    logger.info(f"Chapter {current_chapter['id']}: {current_chapter['title']} "
                              f"(Pages {current_chapter['pdf_page_start']}-{current_chapter['pdf_page_end']})")
                
                self.toc_data["total_pdf_pages"] = total_pages
                
        except Exception as e:
            logger.error(f"Error mapping pages: {e}")
            raise
        
        logger.info("Page mapping complete")
        return self.toc_data
    
    def validate_page_ranges(self) -> bool:
        """
        Validate that page ranges don't overlap and are within bounds
        
        Returns:
            True if valid, False otherwise
        """
        chapters = self.toc_data["chapters"]
        
        for i, chapter in enumerate(chapters):
            start = chapter["pdf_page_start"]
            end = chapter["pdf_page_end"]
            
            # Check valid range
            if start >= end:
                logger.error(f"Invalid range for chapter {chapter['id']}: {start}-{end}")
                return False
            
            # Check no overlap with next chapter
            if i < len(chapters) - 1:
                next_start = chapters[i + 1]["pdf_page_start"]
                if end >= next_start:
                    logger.error(f"Overlap detected between chapters {chapter['id']} and {chapters[i+1]['id']}")
                    return False
        
        logger.info("Page ranges validated successfully")
        return True