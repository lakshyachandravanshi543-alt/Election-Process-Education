import os
import logging
from typing import Tuple
from flask import Flask, render_template, request, jsonify, Response
from flask_talisman import Talisman
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import google.cloud.logging
from dotenv import load_dotenv

from services.gemini_service import get_gemini_response

# Google Services: Initialize Cloud Logging for production environments
try:
    client = google.cloud.logging.Client()
    client.setup_logging()
except Exception:
    pass # Fallback to standard Python logging if not on GCP

# Configure proper application logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-dev-key")

# Security: Set HTTPS headers and Content Security Policy
csp = {
    'default-src': [
        '\'self\'',
        'https://fonts.googleapis.com',
        'https://fonts.gstatic.com'
    ],
    'style-src': [
        '\'self\'',
        'https://fonts.googleapis.com',
        '\'unsafe-inline\'' # allow inline styles if needed
    ]
}
Talisman(app, content_security_policy=csp, force_https=False) # force_https=False for easier local dev

# Efficiency: GZip compression for all responses
Compress(app)

# Security: API Rate Limiting to prevent abuse
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Efficiency: Caching for repetitive identical queries
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

@app.route("/", methods=["GET"])
def index() -> str:
    """
    Render the main chat interface template.
    Returns:
        str: HTML string of the rendered interface.
    """
    logger.info("Serving index page to client.")
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
@limiter.limit("10 per minute") # Specific limit for chat to prevent spam
def chat() -> Tuple[Response, int]:
    """
    Handle incoming chat requests from the frontend, sanitize input, and route to Gemini Service in an optimized manner.
    
    Returns:
        Tuple[Response, int]: JSON response with status, and HTTP status code.
    """
    data = request.get_json()
    
    if not data or "message" not in data:
        logger.warning("Invalid request format received at /api/chat.")
        return jsonify({"error": "Invalid request. 'message' field is required."}), 400
        
    user_message = str(data["message"])[:1000] # Input sanitization: limit length
    chat_history = data.get("history", []) # Optional history for context
    
    # Efficiency: Cache key based on message and history length
    cache_key = f"chat_{hash(user_message)}_{len(chat_history)}"
    cached_response = cache.get(cache_key)
    if cached_response:
        logger.info("Serving chat response from cache.")
        return jsonify({
            "response": cached_response,
            "status": "success",
            "cached": True
        }), 200

    try:
        logger.info(f"Processing chat request. Input length: {len(user_message)}")
        
        # Get AI response
        ai_response = get_gemini_response(user_message, chat_history)
        
        # Store in cache
        cache.set(cache_key, ai_response)
        
        logger.info("Successfully retrieved Gemini response.")
        return jsonify({
            "response": ai_response,
            "status": "success",
            "cached": False
        }), 200
        
    except Exception as e:
        logger.error(f"Error handling /api/chat request: {e}", exc_info=True)
        return jsonify({
            "error": "I'm having trouble processing that right now. Please try again later.",
            "status": "error"
        }), 500

if __name__ == "__main__":
    logger.info("Initializing Flask App...")
    app.run(debug=True, port=5000)
