"""
Validation utilities for NeuroRAG
"""
import re
from typing import Optional
from pathlib import Path

def validate_pdf_path(pdf_path: Path) -> bool:
    """Validate PDF file exists and is readable"""
    return pdf_path.exists() and pdf_path.suffix.lower() == '.pdf'

def validate_query(query: str) -> Optional[str]:
    """
    Validate user query
    
    Returns:
        Cleaned query or None if invalid
    """
    if not query or not isinstance(query, str):
        return None
    
    # Clean query
    query = query.strip()
    
    # Check length
    if len(query) < 3:
        return None
    
    if len(query) > 500:
        query = query[:500]
    
    return query

def validate_mode(mode: str) -> bool:
    """Validate response mode"""
    return mode in ['clinician', 'patient']

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces and special chars with underscore
    filename = re.sub(r'[\s\-]+', '_', filename)
    # Lowercase
    filename = filename.lower()
    return filename