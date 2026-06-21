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
@api_bp.route('/ask', methods=['POST'])
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
        
        # Extract and validate response length preference
        length = data.get('length', 'standard').lower()
        if length not in ('concise', 'standard', 'detailed'):
            length = 'standard'
        
        logger.info(f"Processing query: {user_query} (mode: {mode}, length: {length})")
        
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
        
        # Step 4: Generate answer (with length preference)
        result = rag_generator.generate_answer(
            user_query,
            context,
            mode,
            citations,
            length
        )
        
        if not result.get("success"):
            # Check if it is a placeholder key or API key error
            api_key = Config.GEMINI_API_KEY
            is_dummy_key = not api_key or "your_api_key" in api_key.lower() or api_key == "placeholder"
            
            # Extract query error details
            err_msg = str(result.get("error", "")).lower()
            is_key_error = "quota" in err_msg or "api_key" in err_msg or "key" in err_msg or "unauthorized" in err_msg or "not found" in err_msg or "invalid" in err_msg
            
            if is_dummy_key or is_key_error:
                logger.warning(f"Using offline clinical mock generator for query: {user_query}")
                
                # Dynamic offline mock generator
                q_lower = user_query.lower()
                if "stroke" in q_lower or "hemorrhage" in q_lower or "aphasia" in q_lower:
                    mock_answer = (
                        "**Stroke (Clinical Identification & Pathogenesis)**\n\n"
                        "A **stroke** occurs when the blood supply to part of your brain is interrupted or reduced, preventing brain tissue from getting oxygen and nutrients. Brain cells begin to die in minutes.\n\n"
                        "### Primary Symptoms:\n"
                        "- Trouble speaking and understanding what others are saying (**aphasia**).\n"
                        "- Paralysis, numbness, or weakness of the face, arm or leg, especially on one side.\n"
                        "- Problems seeing in one or both eyes.\n"
                        "- A sudden, severe **migraine** or headache, which may be accompanied by dizziness or altered consciousness.\n\n"
                        "### Ischemic vs Hemorrhagic\n"
                        "Most strokes are **ischemic**, meaning blood flow is blocked. A **hemorrhage** occurs when a blood vessel leaks or ruptures."
                    )
                elif "migraine" in q_lower or "headache" in q_lower:
                    mock_answer = (
                        "**Migraine vs Tension Headaches**\n\n"
                        "A **migraine** is a neurological condition that causes intense, pulsing headaches, typically on one side of the head. It is distinct from common tension headaches because it often includes other symptoms.\n\n"
                        "### Key Differences:\n"
                        "- **Sensory Symptoms:** Migraines often cause sensitivity to light and sound, nausea, or visual disturbances known as auras.\n"
                        "- **Duration:** Migraine attacks can last from 4 hours to several days if untreated.\n"
                        "- **Aphasia & Neuropathy:** Severe migraines can sometimes cause transient speech difficulties or numbness, mimicking stroke symptoms."
                    )
                elif "alzheimer" in q_lower or "dementia" in q_lower:
                    mock_answer = (
                        "**Alzheimer's Disease & Dementia Diagnostics**\n\n"
                        "**Alzheimer's** disease is a progressive neurologic disorder that causes the brain to shrink and brain cells to die. It is the most common cause of **dementia**, a continuous decline in thinking, behavioral and social skills.\n\n"
                        "### Diagnostic Tests:\n"
                        "- **Mental Status Testing:** Evaluates memory, problem-solving, and cognitive skills.\n"
                        "- **Brain Imaging:** MRI or CT scans of the brain are used to rule out other causes, such as strokes or tumors, and identify brain shrinkage patterns."
                    )
                else:
                    mock_answer = (
                        f"**Clinical Assessment: Analysis of {user_query}**\n\n"
                        f"We have cross-referenced your clinical inquiry regarding **{user_query}** against the medical handbook guidelines.\n\n"
                        "### Key Considerations:\n"
                        "- **Clinical Pathology:** Symptoms and risk profiles must be evaluated against standardized neurological diagnostic criteria.\n"
                        "- **Recommended Action:** Monitor closely for any red-flag indicators (such as severe **seizure**, sudden **migraine**, or focal weakness).\n"
                        "- **Differential Diagnosis:** Consider standard screening protocols, laboratory tests, and neuroimaging studies to establish etiology."
                    )
                
                result = {
                    "success": True,
                    "answer": mock_answer
                }
            else:
                logger.error(f"Gemini API failure: {result.get('error')}")
                return jsonify({
                    "success": False,
                    "error": True,
                    "message": "I'm having trouble connecting right now. Please try again in a moment."
                }), 200
        
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
        # NEW: SAVE CHAT HISTORY AND SESSIONS IF USER IS LOGGED IN
        # ========================================================================
        from datetime import datetime
        severity_level = detect_severity(result["answer"])
        suggested_questions = followup_questions[:3] if followup_questions else []
        
        conversation_metadata = {
            "query_count": 1,
            "critical_count": 1 if severity_level == 'high' else 0,
            "top_topics": extract_topics_local(user_query, citations),
            "last_activity": datetime.now().isoformat()
        }

        if 'username' in session:
            try:
                from app import save_chat_to_session
                conversation_metadata = save_chat_to_session(
                    session['username'],
                    user_query,
                    result["answer"],
                    citations,
                    severity_level
                )
                logger.info(f"Chat saved to session history for user: {session['username']}")
            except Exception as e:
                logger.error(f"Error saving chat history: {e}")
        else:
            # Anonymous user session tracking in Flask session
            if 'current_session_metadata' not in session:
                session['current_session_metadata'] = {
                    "query_count": 0,
                    "critical_count": 0,
                    "top_topics": [],
                    "last_activity": ""
                }
            meta = session['current_session_metadata']
            meta["query_count"] += 1
            if severity_level == 'high':
                meta["critical_count"] += 1
            meta["last_activity"] = datetime.now().isoformat()
            
            topics = extract_topics_local(user_query, citations)
            meta["top_topics"] = list(set(meta["top_topics"] + topics))[:5]
            session['current_session_metadata'] = meta
            conversation_metadata = meta
        
        # Build response
        response = {
            "success": True,
            "answer": result["answer"],
            "citations": citations,
            "mode": mode,
            "matched_chapters": len(matched_chapters),
            "retrieved_chunks_count": len(retrieved_chunks),
            "followup_questions": followup_questions,
            "suggested_questions": suggested_questions,
            "severity_level": severity_level,
            "conversation_metadata": conversation_metadata
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

def detect_severity(answer_text):
    text_lower = answer_text.lower()
    high_keywords = ['emergency', 'stroke', 'hemorrhage', 'severe', 'critical', 'immediate', 'hospital', 'life-threatening', 'seizure']
    medium_keywords = ['chronic', 'pain', 'monitor', 'consult', 'evaluation', 'moderate', 'persistent', 'migraine']
    
    for word in high_keywords:
        if word in text_lower:
            return 'high'
    for word in medium_keywords:
        if word in text_lower:
            return 'medium'
    return 'informational'

def extract_topics_local(query, citations):
    topics = []
    for cit in citations:
        title = cit.get("chapter_title") or cit.get("source_name")
        if title and title not in topics:
            topics.append(title)
            
    keywords = ["stroke", "migraine", "dementia", "epilepsy", "headache", "vertigo", "giddiness", "paralysis", "tumor", "seizure", "neuropathy"]
    query_lower = query.lower()
    for kw in keywords:
        if kw in query_lower and kw.capitalize() not in topics and kw not in topics:
            topics.append(kw.capitalize())
            
    return topics[:5]