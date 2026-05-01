import pytest
from unittest.mock import patch, MagicMock
from services.gemini_service import get_gemini_response, _mock_response

def test_mock_response():
    """Test deterministic offline response behaviors."""
    assert "register" in _mock_response("How do I register?")
    assert "Tuesday" in _mock_response("When is the election date?")
    assert "Hello" in _mock_response("Random text")

@patch('services.gemini_service.USE_MOCK', True)
def test_get_gemini_response_mock():
    """Test the mocked service integration directly."""
    res = get_gemini_response("register")
    assert "register" in res

@patch('services.gemini_service.USE_MOCK', False)
@patch('services.gemini_service.genai.GenerativeModel')
def test_get_gemini_response_live(mock_model):
    """Test standard Gemini API invocation mechanics and response extraction."""
    mock_instance = MagicMock()
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is a real AI response about elections."
    
    mock_chat.send_message.return_value = mock_response
    mock_instance.start_chat.return_value = mock_chat
    mock_model.return_value = mock_instance
    
    history = [{"role": "user", "content": "hi"}]
    res = get_gemini_response("test message", chat_history=history)
    
    assert res == "This is a real AI response about elections."
    mock_chat.send_message.assert_called_once()
