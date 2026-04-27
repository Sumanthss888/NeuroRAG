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

def save_chat_history(username, question, answer):
    """Save chat to user's history"""
    try:
        data = load_users()
        if username in data["users"]:
            chat_entry = {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "answer": answer
            }
            data["users"][username]["chat_history"].append(chat_entry)
            
            # Keep only last 100 chats
            if len(data["users"][username]["chat_history"]) > 100:
                data["users"][username]["chat_history"] = data["users"][username]["chat_history"][-100:]
            
            save_users(data)
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")


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
            save_chat_history(session['username'], question, answer)
            return jsonify({'success': True})
    
    return jsonify({'success': False})


if __name__ == '__main__':
    logger.info(f"Starting NeuroRAG server on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )