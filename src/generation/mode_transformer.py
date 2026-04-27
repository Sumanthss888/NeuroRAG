"""
Transform responses between clinician and patient modes
"""
from typing import Dict
from google import genai
from ..utils.config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ModeTransformer:
    """Transform responses between different modes"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key)
        self.model = Config.GEMINI_GENERATION_MODEL
    
    def transform_to_patient_mode(self, technical_text: str) -> str:
        """
        Transform technical medical text to patient-friendly language
        
        Args:
            technical_text: Technical medical text
        
        Returns:
            Patient-friendly text
        """
        prompt = f"""Transform this medical text into simple, patient-friendly language:

MEDICAL TEXT:
{technical_text}

INSTRUCTIONS:
1. Use everyday language instead of medical jargon
2. Explain complex terms with simple analogies
3. Keep it accurate but easy to understand
4. Make it conversational and reassuring
5. Keep the same structure and key information

SIMPLIFIED VERSION:"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if response and response.text:
                return response.text
            
            return technical_text  # Fallback to original
            
        except Exception as e:
            logger.error(f"Error transforming to patient mode: {e}")
            return technical_text
    
    def transform_to_clinician_mode(self, simple_text: str) -> str:
        """
        Transform simple text to technical medical language
        
        Args:
            simple_text: Simple language text
        
        Returns:
            Technical medical text
        """
        prompt = f"""Transform this simple text into precise medical terminology:

SIMPLE TEXT:
{simple_text}

INSTRUCTIONS:
1. Use accurate medical terminology
2. Include relevant clinical details
3. Maintain professional medical language
4. Add specificity where appropriate
5. Keep the same structure and key information

MEDICAL VERSION:"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if response and response.text:
                return response.text
            
            return simple_text  # Fallback to original
            
        except Exception as e:
            logger.error(f"Error transforming to clinician mode: {e}")
            return simple_text
    
    def validate_mode(self, mode: str) -> str:
        """
        Validate and normalize mode
        
        Args:
            mode: Mode string
        
        Returns:
            Valid mode string
        """
        mode = mode.lower().strip()
        
        if mode in ["clinician", "doctor", "medical", "professional"]:
            return "clinician"
        elif mode in ["patient", "simple", "layman", "general"]:
            return "patient"
        else:
            logger.warning(f"Unknown mode: {mode}, defaulting to patient")
            return "patient"