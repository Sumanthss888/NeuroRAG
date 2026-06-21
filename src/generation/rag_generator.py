"""
Generate answers using Gemini with RAG context
"""
from typing import List, Dict, Optional
from google import genai
from google.genai import types
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class RAGGenerator:
    """Generate answers using Gemini with retrieved context"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        
        if not self.api_key or "your_api_key" in self.api_key.lower() or self.api_key == "placeholder":
            self.client = None
            logger.warning("Gemini API key is missing or placeholder. Generator running in offline mode.")
        else:
            try:
                # Initialize Gemini client
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")
                self.client = None
        self.model = Config.GEMINI_GENERATION_MODEL
        
        logger.info(f"Initialized RAG Generator with model: {self.model} (Client active: {self.client is not None})")
    
    # Response length instructions injected into the prompt
    LENGTH_INSTRUCTIONS = {
        "concise": (
            "Be concise and to the point. "
            "Provide a focused summary of the most critical information only. "
            "Target 80-120 words. Use bullet points sparingly — only when truly needed."
        ),
        "standard": (
            "Provide a balanced, well-structured response covering the key points. "
            "Target 200-300 words. Use markdown headers and bullet lists for clarity."
        ),
        "detailed": (
            "Provide a comprehensive, thorough response covering all relevant aspects including "
            "pathophysiology, clinical features, diagnosis, and management where applicable. "
            "Target 400-600 words. Use markdown with headers, sub-headers, and detailed bullet points."
        )
    }

    def generate_answer(self, query: str, context: str, 
                       mode: str = "patient",
                       citations: List[Dict] = None,
                       length: str = "standard") -> Dict:
        """
        Generate answer using RAG
        
        Args:
            query: User query
            context: Retrieved context from chunks
            mode: Response mode (clinician/patient)
            citations: List of citation dictionaries
        
        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Generating answer in {mode} mode, length: {length}")
        
        # Build prompt based on mode and length
        prompt = self._build_prompt(query, context, mode, length)
        
        try:
            if not self.client:
                logger.warning("Offline Mode: Returning failure to trigger routes mock fallback.")
                return {
                    "success": False,
                    "error": "API Key is missing or placeholder"
                }
                
            # Generate response
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if response and response.text:
                answer = response.text
                
                # Add citations to answer
                if citations:
                    answer = self._add_citations(answer, citations)
                
                result = {
                    "success": True,
                    "answer": answer,
                    "mode": mode,
                    "citations": citations or [],
                    "model": self.model
                }
                
                logger.info("Answer generated successfully")
                return result
            else:
                logger.error("No response from Gemini")
                return {
                    "success": False,
                    "error": "No response generated"
                }
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_prompt(self, query: str, context: str, mode: str, length: str = "standard") -> str:
        """
        Build RAG prompt
        
        Args:
            query: User query
            context: Retrieved context
            mode: Response mode
            length: Response length preference (concise/standard/detailed)
        
        Returns:
            Formatted prompt
        """
        mode_config = Config.MODES.get(mode, Config.MODES["patient"])
        mode_instruction = mode_config["prompt_suffix"]
        
        # Get length instruction, default to standard if invalid value provided
        length_instruction = self.LENGTH_INSTRUCTIONS.get(
            length.lower() if length else "standard",
            self.LENGTH_INSTRUCTIONS["standard"]
        )
        
        prompt = f"""You are a medical AI assistant specializing in neurological disorders.

CONTEXT (from "Neurological Disorders – A Handbook for Family Physicians"):
{context}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Answer the question based ONLY on the provided context
2. If the context doesn't contain enough information, say so clearly
3. {mode_instruction}
4. Be accurate and cite specific information from the text
5. RESPONSE LENGTH: {length_instruction}
6. Use clear, well-structured markdown formatting

ANSWER:"""
        
        return prompt
    
    def _add_citations(self, answer: str, citations: List[Dict]) -> str:
        """
        Add citations to answer
        
        Args:
            answer: Generated answer
            citations: List of citations
        
        Returns:
            Answer with citations appended
        """
        if not citations:
            return answer
        
        citation_text = "\n\n---\n**Sources:**\n"
        
        for i, citation in enumerate(citations, 1):
            chapter_title = citation.get("chapter_title", "Unknown")
            chapter_id = citation.get("chapter_id", "")
            
            citation_text += f"{i}. Chapter {chapter_id}: {chapter_title}\n"
        
        return answer + citation_text
    
    def generate_followup_questions(self, query: str, answer: str) -> List[str]:
        """
        Generate follow-up questions based on query and answer
        
        Args:
            query: Original query
            answer: Generated answer
        
        Returns:
            List of follow-up questions
        """
        if not self.client:
            logger.warning("Offline Mode: Returning empty list for follow-up questions.")
            return []
            
        prompt = f"""Based on this medical Q&A, suggest 3 relevant follow-up questions:
 
 ORIGINAL QUESTION:
 {query}
 
 ANSWER PROVIDED:
 {answer}
 
 Generate 3 specific, medically relevant follow-up questions that a patient or clinician might ask. Return only the questions, numbered 1-3."""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if response and response.text:
                # Parse questions
                lines = response.text.strip().split('\n')
                questions = [line.strip() for line in lines if line.strip() and any(c.isalpha() for c in line)]
                
                # Clean up numbering
                questions = [q.lstrip('0123456789. ') for q in questions]
                
                return questions[:3]
            
            return []
            
        except Exception as e:
            logger.warning(f"Error generating follow-up questions: {e}")
            return []
 
    def generate_session_summary(self, chats: List[Dict]) -> str:
        """
        Generate a session summary from history of chats
        """
        if not chats:
            return ""
            
        if not self.client:
            logger.warning("Offline Mode: Returning fallback summary for session.")
            return "Clinical session complete."
            
        summary_prompt = "Generate a concise 1-2 sentence medical summary of the following query session:\n"
        for idx, chat in enumerate(chats, 1):
            q = chat.get("question", chat.get("query", ""))
            summary_prompt += f"Inquiry {idx}: {q}\n"
            
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=summary_prompt
            )
            if response and response.text:
                return response.text.strip()
            return "Session complete."
        except Exception as e:
            logger.warning(f"Error generating session summary: {e}")
            return "Session complete."