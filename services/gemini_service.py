import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Determine if we should mock the API based on key availability
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
USE_MOCK = not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here"

if not USE_MOCK:
    genai.configure(api_key=GEMINI_API_KEY)

# Define the system prompt constraint to ensure the bot stays on topic
SYSTEM_INSTRUCTION = """
You are an intelligent, empathetic, and knowledgeable Election Education Assistant.
Your primary goal is to help users understand the election process, voting timelines, registration steps, and civic engagement.

Guidelines:
1. Provide accurate, non-partisan, and clear information.
2. If a user asks about specific political candidates or opinions, gently remind them that your role is strictly to explain the *process* of voting, not to endorse or evaluate candidates.
3. Keep responses concise and easy to read. Use bullet points or numbered lists where appropriate for step-by-step instructions.
4. If a user asks something completely unrelated to voting or elections, politely steer the conversation back to voter education.
5. Emphasize that rules may vary by state/locality (especially in the US), so always encourage them to check with their local election office.
"""

def get_gemini_response(user_message: str, chat_history: list = None) -> str:
    """
    Send a message to Google Gemini API and get a response aligned with voter education.
    """
    if USE_MOCK:
        # Return a mock response if no API key is configured
        print("WARNING: Using mocked Gemini response because GEMINI_API_KEY is missing.")
        return _mock_response(user_message)
    
    try:
        # Initialize a generative model. gemini-1.5-flash is good for quick, text-based chat.
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_INSTRUCTION)
        
        # Build conversational context
        # Gemini expects history as a list of dictionaries with 'role' (user/model) and 'parts'
        formatted_history = []
        if chat_history:
             for msg in chat_history:
                   # Standardize role names for Gemini (user and model)
                   role = "user" if msg.get("role") == "user" else "model"
                   formatted_history.append({
                       "role": role,
                       "parts": [msg.get("content", "")]
                   })
        
        # Start a chat session with history
        chat = model.start_chat(history=formatted_history)
        
        # Send the new message
        response = chat.send_message(user_message)
        return response.text
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Re-raise to be handled by the route
        raise e

def _mock_response(message: str) -> str:
    """Provides a dummy response when API key is missing."""
    lower_msg = message.lower()
    if "register" in lower_msg:
        return "To register to vote, you typically need to visit your state's election website. Most states allow online registration. You will usually need a valid driver's license or state ID. **Note: This is a simulated response as the Gemini API key is missing.**"
    elif "when" in lower_msg or "date" in lower_msg:
        return "General elections are typically held on the first Tuesday following the first Monday in November. However, primaries and local elections happen throughout the year. **Note: This is a simulated response.**"
    else:
        return "Hello! I am your Election Process Assistant. I can help you understand how to register, when to vote, and the steps involved in the process. Ask me anything! *(Mock Demo Mode)*"
