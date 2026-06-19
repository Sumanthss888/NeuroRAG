"""
Main Flask application for NeuroRAG
"""
from flask import Flask, session, redirect, url_for, request, jsonify, render_template
from flask_cors import CORS
from pathlib import Path
from datetime import timedelta, datetime
import json
import hashlib
from functools import wraps
from src.api.routes import api_bp, init_components
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Users file path
USERS_FILE = Path("users.json")

def init_users_file():
    """Create users.json if it doesn't exist"""
    if not USERS_FILE.exists():
        USERS_FILE.write_text(json.dumps({"users": {}}, indent=2))
        logger.info("✓ Created users.json")

def load_users():
    """Load users from file"""
    init_users_file()
    try:
        return json.loads(USERS_FILE.read_text())
    except:
        return {"users": {}}

def save_users(data):
    """Save users to file"""
    USERS_FILE.write_text(json.dumps(data, indent=2))

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def save_chat_to_session(username, question, answer, citations, severity_level):
    """Save chat to user's active session and update statistics"""
    try:
        data = load_users()
        user = data["users"].get(username)
        if not user:
            return {}
            
        # Ensure sessions and chat_history exist
        if "sessions" not in user:
            user["sessions"] = []
        if "chat_history" not in user:
            user["chat_history"] = []
            
        # Get active session ID from Flask session
        session_id = session.get('current_session_id')
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            session['current_session_id'] = session_id
            
        # Find active session
        active_sess = None
        for s in user["sessions"]:
            if s.get("session_id") == session_id:
                active_sess = s
                break
                
        # If not found, create new session entry
        if not active_sess:
            active_sess = {
                "session_id": session_id,
                "summary": "",
                "query_count": 0,
                "critical_count": 0,
                "top_topics": [],
                "last_activity": datetime.now().isoformat(),
                "chats": []
            }
            user["sessions"].append(active_sess)
            
        # Append chat to chats list
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "mode": session.get('mode', 'patient'),
            "citations": citations,
            "severity_level": severity_level
        }
        active_sess["chats"].append(chat_entry)
        
        # Update statistics
        active_sess["query_count"] = len(active_sess["chats"])
        active_sess["critical_count"] = sum(1 for c in active_sess["chats"] if c.get("severity_level") == 'high')
        active_sess["last_activity"] = datetime.now().isoformat()
        
        # Extract topics
        topics = []
        for cit in citations:
            t = cit.get("chapter_title") or cit.get("source_name")
            if t and t not in topics:
                topics.append(t)
        keywords = ["stroke", "migraine", "dementia", "epilepsy", "headache", "vertigo", "giddiness", "paralysis", "tumor", "seizure", "neuropathy"]
        q_lower = question.lower()
        for kw in keywords:
            if kw in q_lower and kw.capitalize() not in topics and kw not in topics:
                topics.append(kw.capitalize())
        
        active_sess["top_topics"] = list(set(active_sess.get("top_topics", []) + topics))[:5]
        
        # Append to legacy flat chat_history for backward compatibility
        legacy_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer
        }
        user["chat_history"].append(legacy_entry)
        if len(user["chat_history"]) > 100:
            user["chat_history"] = user["chat_history"][-100:]
            
        save_users(data)
        
        # Return conversation metadata contract
        return {
            "query_count": active_sess["query_count"],
            "critical_count": active_sess["critical_count"],
            "top_topics": active_sess["top_topics"],
            "last_activity": active_sess["last_activity"]
        }
    except Exception as e:
        logger.error(f"Error saving chat to session: {e}")
        return {}

def load_conversations(username):
    """Load and sanitize conversations/sessions for a user with fallback migration"""
    data = load_users()
    user = data["users"].get(username, {})
    
    sessions = user.get("sessions", [])
    
    # Check if sessions exist, otherwise migrate legacy flat chat_history
    if not sessions and user.get("chat_history"):
        sessions = [{
            "session_id": "legacy-session",
            "summary": "",
            "query_count": len(user["chat_history"]),
            "critical_count": 0,
            "top_topics": [],
            "last_activity": datetime.now().isoformat(),
            "chats": user["chat_history"]
        }]
        user["sessions"] = sessions
        save_users(data)
        
    # Sanitize and apply default fallback values for backward compatibility
    current_timestamp = datetime.now().isoformat()
    for sess in sessions:
        if "summary" not in sess: sess["summary"] = ""
        if "query_count" not in sess: sess["query_count"] = len(sess.get("chats", []))
        if "critical_count" not in sess: sess["critical_count"] = 0
        if "top_topics" not in sess: sess["top_topics"] = []
        if "last_activity" not in sess: sess["last_activity"] = current_timestamp
        
    return sessions


def create_app():
    """Create and configure Flask app"""
    
    # Create Flask app
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    
    # Enable CORS
    CORS(app)
    
    # Load configuration
    app.config['SECRET_KEY'] = 'neurorag-secret-key-change-in-production'
    app.config['JSON_SORT_KEYS'] = False
    
    # Session configuration for authentication
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Create necessary directories
    Config.create_directories()
    
    # Validate configuration
    try:
        Config.validate_config()
        logger.info("✓ Configuration validated")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    # Initialize RAG components
    logger.info("Initializing RAG components...")
    if not init_components():
        logger.error("Failed to initialize RAG components")
        # Continue anyway - might be in setup mode
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    logger.info("✓ Flask app created successfully")
    
    return app


app = create_app()
init_users_file()
    
@app.before_request
def require_login():
    """Redirect to login if not authenticated"""
    # Allow access to login, signup, and static files without authentication
    allowed_routes = ['login', 'signup', 'static']
    
    if request.endpoint and request.endpoint not in allowed_routes:
        if 'username' not in session:
            return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if request.method == 'GET':
        if 'username' in session:
            return redirect('/')
        return render_template('login.html')
    
    # POST - handle login
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    users_data = load_users()
    
    if username not in users_data["users"]:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    user = users_data["users"][username]
    
    if user["password"] != hash_password(password):
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    session['username'] = username
    session.permanent = True
    logger.info(f"✓ User logged in: {username}")
    
    return jsonify({'success': True, 'message': 'Login successful'})

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page and registration"""
    if request.method == 'GET':
        if 'username' in session:
            return redirect('/')
        return render_template('signup.html')
    
    # POST - handle signup
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    if len(username) < 3:
        return jsonify({'success': False, 'message': 'Username must be at least 3 characters'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    users_data = load_users()
    
    if username in users_data["users"]:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    # Create new user
    users_data["users"][username] = {
        "password": hash_password(password),
        "email": email,
        "created_at": datetime.now().isoformat(),
        "chat_history": []
    }
    
    save_users(users_data)
    logger.info(f"✓ New user registered: {username}")
    
    return jsonify({'success': True, 'message': 'Account created successfully'})

@app.route('/logout')
def logout():
    """Logout user"""
    username = session.get('username', 'Unknown')
    session.pop('username', None)
    logger.info(f"✓ User logged out: {username}")
    return redirect('/login')

@app.route('/chat_history')
@login_required
def chat_history():
    """View chat history"""
    username = session.get('username')
    users_data = load_users()
    
    history = []
    if username in users_data["users"]:
        history = list(reversed(users_data["users"][username]["chat_history"]))
    
    return render_template('chat_history.html', username=username, history=history)

@app.route('/api/clear_history', methods=['POST'])
@login_required
def clear_history():
    """Clear user's chat history"""
    username = session.get('username')
    users_data = load_users()
    
    if username in users_data["users"]:
        users_data["users"][username]["chat_history"] = []
        save_users(users_data)
        logger.info(f"✓ Chat history cleared for: {username}")
    
    return jsonify({'success': True, 'message': 'Chat history cleared'})

@app.route('/api/save_chat', methods=['POST'])
def api_save_chat():
    """Save chat from existing chat route"""
    if 'username' in session:
        data = request.get_json()
        question = data.get('question', '')
        answer = data.get('answer', '')
        
        if question and answer:
            save_chat_to_session(session['username'], question, answer, [], 'informational')
            return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/dashboard')
@login_required
def dashboard():
    """View metrics dashboard"""
    username = session.get('username')
    sessions_list = load_conversations(username)
    
    from src.utils.analytics import AnalyticsService
    metrics = AnalyticsService.get_aggregates(sessions_list)
    
    return render_template('dashboard.html', username=username, metrics=metrics)

@app.route('/api/end_session', methods=['POST'])
@login_required
def end_session():
    """End current chat session and summarize"""
    username = session.get('username')
    session_id = session.get('current_session_id')
    
    if not session_id:
        return jsonify({'success': False, 'message': 'No active session'})
        
    data = load_users()
    user = data["users"].get(username)
    if not user or "sessions" not in user:
        return jsonify({'success': False, 'message': 'User session not found'})
        
    # Find active session
    active_sess = None
    for s in user["sessions"]:
        if s.get("session_id") == session_id:
            active_sess = s
            break
            
    if not active_sess:
        return jsonify({'success': False, 'message': 'Active session not found'})
        
    # Generate summary once per session
    summary = active_sess.get("summary", "")
    if not summary and active_sess.get("chats"):
        try:
            from src.api.routes import rag_generator
            if rag_generator:
                summary = rag_generator.generate_session_summary(active_sess["chats"])
            else:
                summary = "Clinical session complete."
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            summary = "Clinical session complete."
            
        active_sess["summary"] = summary
        save_users(data)
        
    # Clear session ID from Flask session so a new query starts a fresh session
    session.pop('current_session_id', None)
    session.pop('current_session_metadata', None)
    
    return jsonify({
        'success': True, 
        'summary': summary or "Clinical session complete.",
        'session_id': session_id
    })

@app.route('/api/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Fetch all conversations/sessions for the user"""
    username = session.get('username')
    sessions_list = load_conversations(username)
    
    return jsonify({
        'success': True,
        'conversations': list(reversed(sessions_list))
    })


if __name__ == '__main__':
    logger.info(f"Starting NeuroRAG server on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )