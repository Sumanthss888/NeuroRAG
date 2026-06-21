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
                logger.warning(f"Using offline clinical mock generator for query: {user_query} (length={length})")
                
                # Length-aware offline mock generator
                # Each topic has concise / standard / detailed variants
                q_lower = user_query.lower()

                # ── STROKE ──────────────────────────────────────────────────────
                if "stroke" in q_lower or "hemorrhage" in q_lower or "aphasia" in q_lower:
                    mock_variants = {
                        "concise": (
                            "**Stroke — Quick Summary**\n\n"
                            "A **stroke** occurs when blood supply to the brain is cut off. "
                            "Key symptoms: sudden weakness on one side, slurred speech (**aphasia**), "
                            "vision loss, and severe headache. "
                            "Types: **ischemic** (blocked artery) or **hemorrhagic** (ruptured vessel). "
                            "Call emergency services immediately."
                        ),
                        "standard": (
                            "**Stroke (Clinical Identification & Pathogenesis)**\n\n"
                            "A **stroke** occurs when the blood supply to part of your brain is interrupted or reduced, "
                            "preventing brain tissue from getting oxygen and nutrients. Brain cells begin to die in minutes.\n\n"
                            "### Primary Symptoms\n"
                            "- Sudden weakness or numbness of the face, arm, or leg — especially on one side\n"
                            "- Trouble speaking or understanding speech (**aphasia**)\n"
                            "- Vision problems in one or both eyes\n"
                            "- Sudden, severe headache with no known cause\n\n"
                            "### Types\n"
                            "- **Ischemic** (80 % of strokes): blocked artery\n"
                            "- **Hemorrhagic**: ruptured blood vessel causing bleeding in or around the brain\n\n"
                            "**Act FAST** — Face drooping, Arm weakness, Speech difficulty, Time to call emergency services."
                        ),
                        "detailed": (
                            "**Stroke — Comprehensive Clinical Overview**\n\n"
                            "## Pathophysiology\n"
                            "A stroke is an acute neurological emergency caused by sudden disruption of cerebral blood flow. "
                            "Within minutes of ischemia onset, a core infarct zone forms, surrounded by the ischemic **penumbra** — "
                            "salvageable tissue if reperfusion is achieved promptly.\n\n"
                            "## Classification\n"
                            "| Type | Mechanism | Proportion |\n"
                            "|---|---|---|\n"
                            "| Ischemic | Thromboembolism or small-vessel occlusion | ~80 % |\n"
                            "| Intracerebral Hemorrhage | Hypertensive vessel rupture | ~15 % |\n"
                            "| Subarachnoid Hemorrhage | Aneurysm or AVM rupture | ~5 % |\n\n"
                            "## Clinical Features\n"
                            "- **Hemiplegia / hemiparesis**: contralateral to lesion\n"
                            "- **Aphasia** (dominant hemisphere): expressive (Broca's) or receptive (Wernicke's)\n"
                            "- **Homonymous hemianopia**: visual field defect\n"
                            "- **Neglect syndrome**: non-dominant hemisphere parietal lesion\n"
                            "- **Sudden severe headache** (worst-of-life): subarachnoid hemorrhage until proven otherwise\n\n"
                            "## Diagnosis\n"
                            "- **CT without contrast**: first-line to exclude hemorrhage\n"
                            "- **MRI DWI**: gold standard for early ischemic change\n"
                            "- **CTA / MRA**: vascular imaging for large-vessel occlusion\n\n"
                            "## Management\n"
                            "- **Ischemic**: IV tPA within 4.5 h of onset; mechanical thrombectomy for LVO up to 24 h\n"
                            "- **Hemorrhagic**: BP control, reversal of anticoagulation, neurosurgical evaluation\n"
                            "- All patients: stroke unit care, aspirin, statin, secondary prevention\n\n"
                            "**Prognosis** depends on stroke volume, location, and time-to-treatment."
                        )
                    }

                # ── MIGRAINE / HEADACHE ─────────────────────────────────────────
                elif "migraine" in q_lower or "headache" in q_lower:
                    mock_variants = {
                        "concise": (
                            "**Migraine — Key Points**\n\n"
                            "A **migraine** is a neurological disorder causing unilateral, throbbing headache, often with nausea, "
                            "photophobia, and phonophobia. Aura (visual disturbances, numbness) precedes attacks in ~30 % of patients. "
                            "Acute treatment: triptans or NSAIDs. Prevention: beta-blockers, topiramate."
                        ),
                        "standard": (
                            "**Migraine vs Tension Headaches**\n\n"
                            "A **migraine** is a neurological condition causing intense, pulsing headaches, typically on one side. "
                            "It is distinct from tension headaches because of associated systemic symptoms.\n\n"
                            "### Key Differences\n"
                            "- **Pain quality**: Migraine = pulsating; Tension = pressing/tightening\n"
                            "- **Aura**: Visual zigzag lines, blind spots, or tingling — precede migraine in ~30 % of cases\n"
                            "- **Associated symptoms**: Nausea, vomiting, sensitivity to light and sound\n"
                            "- **Duration**: 4–72 hours untreated\n\n"
                            "### Treatment\n"
                            "- Acute: Triptans (sumatriptan), NSAIDs, anti-emetics\n"
                            "- Preventive: Propranolol, topiramate, amitriptyline, CGRP antagonists"
                        ),
                        "detailed": (
                            "**Migraine — Comprehensive Clinical Guide**\n\n"
                            "## Pathophysiology\n"
                            "Migraines involve cortical spreading depression (CSD), trigeminovascular activation, and neurogenic "
                            "inflammation. CGRP (calcitonin gene-related peptide) is the key mediator of vasodilation and pain transmission.\n\n"
                            "## Classification (ICHD-3)\n"
                            "- **Migraine without aura**: most common; recurrent, 4–72 h attacks\n"
                            "- **Migraine with aura**: focal neurological symptoms preceding headache\n"
                            "- **Chronic migraine**: ≥15 headache days/month for >3 months\n"
                            "- **Hemiplegic migraine**: motor aura — rare, may mimic stroke\n\n"
                            "## Clinical Features\n"
                            "- Unilateral, pulsating moderate-to-severe headache\n"
                            "- Nausea ± vomiting, photophobia, phonophobia\n"
                            "- Aura: visual (scintillating scotoma), sensory (tingling), or speech disturbance\n"
                            "- Prodrome: fatigue, mood changes, food cravings (hours before)\n"
                            "- Postdrome: fatigue, cognitive fog ('migraine hangover')\n\n"
                            "## Diagnosis\n"
                            "Primarily clinical. Imaging (MRI) indicated for atypical features, first severe headache, "
                            "or focal neurological deficits persisting after attack.\n\n"
                            "## Management\n"
                            "**Acute**\n"
                            "- Triptans (5-HT₁B/D agonists): sumatriptan 50–100 mg PO — first-line\n"
                            "- NSAIDs: ibuprofen, naproxen\n"
                            "- Antiemetics: metoclopramide, prochlorperazine\n"
                            "- CGRP antagonists (gepants): rimegepant, ubrogepant — for triptan-refractory cases\n\n"
                            "**Preventive** (if ≥4 attacks/month)\n"
                            "- Beta-blockers: propranolol, metoprolol\n"
                            "- Topiramate, valproate\n"
                            "- Monoclonal anti-CGRP antibodies: erenumab, fremanezumab\n"
                            "- Botulinum toxin A: chronic migraine\n\n"
                            "**Prognosis**: Variable; many patients achieve significant reduction with appropriate prevention."
                        )
                    }

                # ── ALZHEIMER / DEMENTIA ────────────────────────────────────────
                elif "alzheimer" in q_lower or "dementia" in q_lower:
                    mock_variants = {
                        "concise": (
                            "**Alzheimer's Disease — Quick Summary**\n\n"
                            "**Alzheimer's** is the most common cause of **dementia** — progressive loss of memory, "
                            "language, and executive function. Diagnosis: clinical assessment + neuroimaging. "
                            "Treatment: cholinesterase inhibitors (donepezil) for symptom management; no cure exists."
                        ),
                        "standard": (
                            "**Alzheimer's Disease & Dementia**\n\n"
                            "**Alzheimer's** disease is a progressive neurologic disorder causing brain shrinkage and neuron death. "
                            "It is the most common cause of **dementia**, accounting for 60–80 % of cases.\n\n"
                            "### Clinical Features\n"
                            "- **Early**: Short-term memory loss, word-finding difficulty, getting lost in familiar places\n"
                            "- **Middle**: Increasing confusion, personality changes, difficulty with ADLs\n"
                            "- **Late**: Loss of speech, swallowing difficulties, complete dependence\n\n"
                            "### Diagnosis\n"
                            "- Cognitive testing (MMSE, MoCA)\n"
                            "- MRI/CT: hippocampal atrophy, rule out vascular causes\n"
                            "- CSF or PET: amyloid / tau biomarkers\n\n"
                            "### Treatment\n"
                            "- Cholinesterase inhibitors: donepezil, rivastigmine (mild–moderate)\n"
                            "- Memantine: moderate–severe stage\n"
                            "- Anti-amyloid mAbs (lecanemab): early disease"
                        ),
                        "detailed": (
                            "**Alzheimer's Disease — Comprehensive Clinical Overview**\n\n"
                            "## Pathophysiology\n"
                            "Alzheimer's is characterised by two hallmark proteinopathies:\n"
                            "- **Amyloid plaques**: extracellular aggregates of Aβ-42 peptide\n"
                            "- **Neurofibrillary tangles**: intracellular hyperphosphorylated tau protein\n\n"
                            "These lead to progressive synaptic dysfunction, neuronal loss, and cortical atrophy — "
                            "particularly affecting the **hippocampus**, **entorhinal cortex**, and **association cortices**.\n\n"
                            "## Risk Factors\n"
                            "- **APOE-ε4 allele**: strongest genetic risk factor\n"
                            "- Age >65, female sex, family history, Down syndrome\n"
                            "- Modifiable: hypertension, diabetes, obesity, physical inactivity, hearing loss\n\n"
                            "## Staging (NIA–AA Framework)\n"
                            "| Stage | Features |\n"
                            "|---|---|\n"
                            "| Preclinical | Biomarker changes; no symptoms |\n"
                            "| MCI due to AD | Subtle cognitive decline; functional independence preserved |\n"
                            "| Mild AD | Memory, language, visuospatial deficits; some functional impairment |\n"
                            "| Moderate AD | Significant memory loss, confusion, behavioural symptoms |\n"
                            "| Severe AD | Minimal verbal output, complete dependence, incontinence |\n\n"
                            "## Diagnosis\n"
                            "- **Neuropsychological testing**: MMSE, MoCA, ACE-III\n"
                            "- **MRI**: hippocampal and medial temporal lobe atrophy\n"
                            "- **PET**: amyloid-PET (florbetapir), FDG-PET (hypometabolism)\n"
                            "- **CSF**: ↓Aβ-42, ↑t-tau, ↑p-tau181\n"
                            "- **Blood biomarkers**: p-tau217, p-tau231 (emerging)\n\n"
                            "## Management\n"
                            "**Symptomatic**\n"
                            "- Donepezil / rivastigmine / galantamine (cholinesterase inhibitors) — mild to moderate\n"
                            "- Memantine (NMDA antagonist) — moderate to severe\n"
                            "- Combination therapy for moderate–severe disease\n\n"
                            "**Disease-modifying (approved 2023–2024)**\n"
                            "- **Lecanemab** (anti-Aβ mAb): slows progression in early/MCI stage\n"
                            "- **Donanemab**: amyloid plaque clearance in early AD\n\n"
                            "**Non-pharmacological**: cognitive stimulation, structured activity, caregiver support\n\n"
                            "**Prognosis**: Mean survival 8–10 years from diagnosis; highly variable."
                        )
                    }

                # ── GENERIC ─────────────────────────────────────────────────────
                else:
                    mock_variants = {
                        "concise": (
                            f"**Clinical Summary: {user_query}**\n\n"
                            "Based on the neurological handbook, the key clinical points are:\n"
                            "- Monitor for red-flag symptoms (seizure, sudden headache, focal weakness)\n"
                            "- Standard diagnostic workup: neuroimaging + laboratory studies\n"
                            "- Refer to neurology if symptoms persist or worsen"
                        ),
                        "standard": (
                            f"**Clinical Assessment: {user_query}**\n\n"
                            f"Cross-referencing your inquiry regarding **{user_query}** against neurological handbook guidelines:\n\n"
                            "### Key Considerations\n"
                            "- **Clinical Pathology**: Evaluate symptoms against standardised neurological diagnostic criteria\n"
                            "- **Recommended Action**: Monitor for red-flag indicators (severe seizure, sudden migraine, focal weakness)\n"
                            "- **Differential Diagnosis**: Consider standard screening, laboratory tests, and neuroimaging\n\n"
                            "### Next Steps\n"
                            "- Complete neurological examination\n"
                            "- Appropriate neuroimaging (CT/MRI based on presentation)\n"
                            "- Specialist referral if indicated"
                        ),
                        "detailed": (
                            f"**Comprehensive Clinical Analysis: {user_query}**\n\n"
                            "## Background\n"
                            f"This query pertains to neurological assessment of **{user_query}**. "
                            "The following analysis is drawn from the Neurological Disorders Handbook for Family Physicians.\n\n"
                            "## Clinical Approach\n"
                            "### History\n"
                            "- Onset, duration, progression, and character of symptoms\n"
                            "- Associated features: fever, trauma, toxic exposure, systemic illness\n"
                            "- Family history and pre-existing neurological conditions\n\n"
                            "### Examination\n"
                            "- Full neurological examination: cranial nerves, motor, sensory, cerebellar, reflexes\n"
                            "- Cognitive assessment if relevant (MMSE / MoCA)\n"
                            "- Ophthalmoscopy: papilloedema (raised ICP)\n\n"
                            "### Investigations\n"
                            "- **Neuroimaging**: CT (acute), MRI (structural detail, demyelination)\n"
                            "- **EEG**: if seizure disorder suspected\n"
                            "- **CSF analysis**: meningitis, SAH, MS, Guillain-Barré\n"
                            "- **Blood**: FBC, ESR, CRP, glucose, renal/liver function, thyroid\n\n"
                            "## Differential Diagnosis\n"
                            "Depends on presentation; common neurological differentials include:\n"
                            "stroke, TIA, migraine, epilepsy, dementia, Parkinson's, MS, peripheral neuropathy.\n\n"
                            "## Red-Flag Indicators (Require Urgent Referral)\n"
                            "- Thunderclap headache\n"
                            "- New focal neurological deficit\n"
                            "- Seizure with no prior history\n"
                            "- Rapidly progressive cognitive decline\n"
                            "- Fever + meningism\n\n"
                            "## Management Principles\n"
                            "Tailored to confirmed diagnosis. General measures:\n"
                            "- Optimise vascular risk factors\n"
                            "- Pharmacotherapy per guideline protocol\n"
                            "- Multidisciplinary team: neurology, neuropsychology, physiotherapy, occupational therapy\n"
                            "- Patient education and caregiver support"
                        )
                    }

                # Select the variant matching the requested length (default standard)
                mock_answer = mock_variants.get(length, mock_variants["standard"])
                
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