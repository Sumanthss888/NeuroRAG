"""
Match user queries to relevant chapters
"""
import json
from typing import List, Dict, Optional
from pathlib import Path
from difflib import SequenceMatcher
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ChapterMatcher:
    """Match queries to relevant chapters using keyword matching"""
    
    def __init__(self, toc_data: Dict = None):
        self.toc_data = toc_data
        
        if not self.toc_data:
            self.load_toc()
    
    def load_toc(self):
        """Load TOC from file"""
        toc_path = Config.TOC_MASTER_PATH
        
        if not toc_path.exists():
            raise FileNotFoundError(f"TOC file not found: {toc_path}")
        
        with open(toc_path, 'r', encoding='utf-8') as f:
            self.toc_data = json.load(f)
        
        logger.info(f"Loaded TOC with {len(self.toc_data['chapters'])} chapters")
    
    def match_chapters(self, query: str, max_chapters: int = None) -> List[Dict]:
        """
        Match query to relevant chapters
        
        Args:
            query: User query
            max_chapters: Maximum chapters to return
        
        Returns:
            List of matched chapter dictionaries with scores
        """
        max_chapters = max_chapters or Config.MAX_MATCHED_CHAPTERS
        
        logger.info(f"Matching query to chapters: {query}")
        
        # Normalize query
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        chapter_scores = []
        
        for chapter in self.toc_data["chapters"]:
            score = self._calculate_match_score(
                query_lower,
                query_words,
                chapter
            )
            
            if score > 0:
                chapter_scores.append({
                    "chapter": chapter,
                    "score": score
                })
        
        # Sort by score (descending)
        chapter_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Take top N
        matched_chapters = chapter_scores[:max_chapters]
        
        logger.info(f"Matched {len(matched_chapters)} chapters:")
        for match in matched_chapters:
            logger.info(f"  - Chapter {match['chapter']['id']}: "
                       f"{match['chapter']['title']} (score: {match['score']:.2f})")
        
        return matched_chapters
    
    def _calculate_match_score(self, query: str, query_words: set, 
                               chapter: Dict) -> float:
        """
        Calculate match score between query and chapter
        
        Args:
            query: Lowercase query string
            query_words: Set of query words
            chapter: Chapter dictionary
        
        Returns:
            Match score (0-1)
        """
        score = 0.0
        
        # Check keywords (highest weight)
        keywords = [kw.lower() for kw in chapter.get("keywords", [])]
        
        for keyword in keywords:
            # Exact keyword match in query
            if keyword in query:
                score += 3.0
            
            # Keyword word match
            keyword_words = set(keyword.split())
            word_overlap = len(query_words & keyword_words)
            if word_overlap > 0:
                score += word_overlap * 1.5
            
            # Fuzzy match
            for query_word in query_words:
                similarity = self._fuzzy_match(query_word, keyword)
                if similarity > Config.KEYWORD_MATCH_THRESHOLD:
                    score += similarity * 0.5
        
        # Check title (medium weight)
        title_lower = chapter["title"].lower()
        
        if any(word in title_lower for word in query_words):
            score += 2.0
        
        # Fuzzy match on title
        title_similarity = self._fuzzy_match(query, title_lower)
        if title_similarity > Config.KEYWORD_MATCH_THRESHOLD:
            score += title_similarity * 1.0
        
        # Check section (low weight)
        section_lower = chapter["section"].lower()
        
        if any(word in section_lower for word in query_words):
            score += 0.5
        
        return score
    
    def _fuzzy_match(self, str1: str, str2: str) -> float:
        """
        Calculate fuzzy similarity between two strings
        
        Args:
            str1: First string
            str2: Second string
        
        Returns:
            Similarity score (0-1)
        """
        return SequenceMatcher(None, str1, str2).ratio()
    
    def get_chapter_by_id(self, chapter_id: int) -> Optional[Dict]:
        """
        Get chapter by ID
        
        Args:
            chapter_id: Chapter ID
        
        Returns:
            Chapter dictionary or None
        """
        for chapter in self.toc_data["chapters"]:
            if chapter["id"] == chapter_id:
                return chapter
        
        return None
    
    def get_all_chapters(self) -> List[Dict]:
        """Get all chapters"""
        return self.toc_data["chapters"]