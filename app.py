import os
import logging
from typing import Tuple
from flask import Flask, render_template, request, jsonify, Response
from flask_talisman import Talisman
from flask_compress import Compress
from dotenv import load_dotenv

from services.gemini_service import get_gemini_response

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
Talisman(app, content_security_policy=csp, force_https=False) # force_https=False for easier local dev, can be True in prod

# Efficiency: GZip compression for all responses
Compress(app)

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
    
    try:
        logger.info(f"Processing chat request. Input length: {len(user_message)}")
        
        # Get AI response
        ai_response = get_gemini_response(user_message, chat_history)
        
        logger.info("Successfully retrieved Gemini response.")
        return jsonify({
            "response": ai_response,
            "status": "success"
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
