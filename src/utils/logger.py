"""
Logging configuration for NeuroRAG
"""
import logging
import sys
from pathlib import Path
from .config import Config

def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(Config.LOG_FORMAT)
    
    # Console handler with UTF-8 encoding for Windows compatibility
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Force UTF-8 encoding for Windows
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass  # If reconfigure fails, continue with default
    
    logger.addHandler(console_handler)
    
    # File handler with UTF-8 encoding
    if Config.LOG_FILE:
        Config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger