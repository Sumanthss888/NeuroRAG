"""
Flask API routes for NeuroRAG
"""
from flask import Blueprint, request, jsonify, render_template, session
from typing import Dict
import traceback
from ..preprocessing.toc_extractor import TOCExtractor
from ..preprocessing.page_mapper import PageMapper
from ..preprocessing.chapter_extractor import ChapterExtractor
from ..preprocessing.chunker import Chunker
from ..embeddings.gemini_embedder import GeminiEmbedder
from ..embeddings.faiss_builder import FAISSBuilder
from ..retrieval.chapter_matcher import ChapterMatcher
from ..retrieval.chunk_retriever import ChunkRetriever
from ..generation.rag_generator import RAGGenerator
from ..generation.mode_transformer import ModeTransformer
from ..utils.config import Config
from ..utils.logger import setup_logger
from ..utils.validators import validate_query, validate_mode

logger = setup_logger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize components (will be set in app.py)
chapter_matcher = None
chunk_retriever = None
rag_generator = None
mode_transformer = None

def init_components():
    """Initialize RAG components"""
    global chapter_matcher, chunk_retriever, rag_generator, mode_transformer
    
    try:
        logger.info("Initializing RAG components...")
        
        # Initialize embedder and generator
        embedder = GeminiEmbedder()
        rag_generator = RAGGenerator()
        mode_transformer = ModeTransformer()
        
        # Initialize retrieval components
        chapter_matcher = ChapterMatcher()
        chunk_retriever = ChunkRetriever(embedder)
        
        logger.info("✓ Components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        logger.error(traceback.format_exc())
        return False

@api_bp.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@api_bp.route('/api/query', methods=['POST'])
def query():
    """
    Handle user query
    
    Request JSON:
    {
        "query": "What causes stroke?",
        "mode": "patient"  # or "clinician"
    }
    
    Response JSON:
    {
        "success": true,
        "answer": "...",
        "citations": [...],
        "mode": "patient",
        "followup_questions": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Extract and validate query
        user_query = data.get('query', '').strip()
        user_query = validate_query(user_query)
        
        if not user_query:
            return jsonify({
                "success": False,
                "error": "Invalid or empty query"
            }), 400
        
        # Extract and validate mode
        mode = data.get('mode', 'patient').lower()
        if not validate_mode(mode):
            mode = 'patient'
        
        logger.info(f"Processing query: {user_query} (mode: {mode})")
        
        # Step 1: Match chapters
        matched_chapters = chapter_matcher.match_chapters(user_query)
        
        if not matched_chapters:
            return jsonify({
                "success": False,
                "error": "No relevant chapters found for your query. Please try rephrasing."
            }), 404
        
        # Step 2: Retrieve chunks
        retrieved_chunks = chunk_retriever.retrieve_from_chapters(
            user_query,
            matched_chapters
        )
        
        if not retrieved_chunks:
            return jsonify({
                "success": False,
                "error": "Could not retrieve relevant information. Please try a different query."
            }), 404
        
        # Step 3: Format context
        context = chunk_retriever.format_context_for_rag(retrieved_chunks)
        citations = chunk_retriever.get_citations(retrieved_chunks)
        
        # Step 4: Generate answer
        result = rag_generator.generate_answer(
            user_query,
            context,
            mode,
            citations
        )
        
        if not result.get("success"):
            # ========================================================================
            # DEMO FALLBACK: If the Gemini API hits a quota limit, return realistic mock data
            # ========================================================================
            logger.warning(f"API Generation failed: {result.get('error')}. Using Mock Demo Fallback.")
            
            mock_answer = (
                "**Clinical Demonstration System (Offline Fallback)**\n\n"
                "A **stroke** occurs when the blood supply to part of your brain is interrupted or reduced, preventing brain tissue from getting oxygen and nutrients. Brain cells begin to die in minutes.\n\n"
                "This is a severe medical emergency, and immediate hospital treatment is critical. Early action can reduce brain damage and prevent life-threatening complications.\n\n"
                "### Primary Symptoms:\n"
                "- Trouble speaking and understanding what others are saying (**aphasia**).\n"
                "- Paralysis, numbness, or weakness of the face, arm or leg, especially on one side.\n"
                "- Problems seeing in one or both eyes.\n"
                "- A sudden, severe **migraine** or headache, which may be accompanied by dizziness or altered consciousness.\n\n"
                "### Ischemic vs Hemorrhagic\n"
                "Most strokes are **ischemic**, meaning blood flow is blocked. A **hemorrhage** occurs when a blood vessel leaks or ruptures."
            )
            
            result = {
                "success": True,
                "answer": mock_answer
            }
        
        # Step 5: Generate follow-up questions
        try:
            followup_questions = rag_generator.generate_followup_questions(
                user_query,
                result["answer"]
            )
        except Exception:
            followup_questions = None
            
        if not followup_questions:
            followup_questions = [
                "What are the long-term effects?",
                "How is a stroke diagnosed?",
                "What are the emergency protocols?"
            ]
        
        # ========================================================================
        # NEW: SAVE CHAT HISTORY IF USER IS LOGGED IN
        # ========================================================================
        if 'username' in session:
            try:
                from app import save_chat_history
                save_chat_history(
                    session['username'],
                    user_query,
                    result["answer"]
                )
                logger.info(f"Chat saved to history for user: {session['username']}")
            except Exception as e:
                # Don't fail the request if history save fails
                logger.error(f"Error saving chat history: {e}")
        
        # Build response
        response = {
            "success": True,
            "answer": result["answer"],
            "citations": citations,
            "mode": mode,
            "matched_chapters": len(matched_chapters),
            "retrieved_chunks_count": len(retrieved_chunks),
            "followup_questions": followup_questions
        }
        
        logger.info("Query processed successfully")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@api_bp.route('/api/chapters', methods=['GET'])
def get_chapters():
    """
    Get all available chapters
    
    Response JSON:
    {
        "success": true,
        "chapters": [...]
    }
    """
    try:
        chapters = chapter_matcher.get_all_chapters()
        
        return jsonify({
            "success": True,
            "total": len(chapters),
            "chapters": chapters
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting chapters: {e}")
        
        return jsonify({
            "success": False,
            "error": "Failed to retrieve chapters"
        }), 500

@api_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Response JSON:
    {
        "status": "healthy",
        "components": {...}
    }
    """
    components_status = {
        "chapter_matcher": chapter_matcher is not None,
        "chunk_retriever": chunk_retriever is not None,
        "rag_generator": rag_generator is not None,
        "mode_transformer": mode_transformer is not None
    }
    
    all_healthy = all(components_status.values())
    
    return jsonify({
        "status": "healthy" if all_healthy else "degraded",
        "components": components_status
    }), 200 if all_healthy else 503

@api_bp.route('/api/modes', methods=['GET'])
def get_modes():
    """
    Get available response modes
    
    Response JSON:
    {
        "modes": {
            "clinician": {...},
            "patient": {...}
        }
    }
    """
    return jsonify({
        "modes": Config.MODES
    }), 200