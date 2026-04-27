from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from services.gemini_service import get_gemini_response

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-dev-key")

@app.route("/", methods=["GET"])
def index():
    """Render the main chat interface."""
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat requests from the frontend."""
    data = request.get_json()
    
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request. 'message' field is required."}), 400
        
    user_message = data["message"]
    chat_history = data.get("history", []) # Optional history for context
    
    try:
        # Get AI response
        ai_response = get_gemini_response(user_message, chat_history)
        
        return jsonify({
            "response": ai_response,
            "status": "success"
        })
    except Exception as e:
        print(f"Error in /api/chat: {e}")
        return jsonify({
            "error": "I'm having trouble processing that right now. Please try again later.",
            "status": "error"
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
