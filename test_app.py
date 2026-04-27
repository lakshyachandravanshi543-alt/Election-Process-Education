import json
import pytest
from app import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the main page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'CivicGuide' in response.data

def test_chat_api_missing_message(client):
    """Test the chat API with missing message payload."""
    response = client.post('/api/chat', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.get_gemini_response')
def test_chat_api_success(mock_gemini, client):
    """Test a successful chat API response."""
    # Mock the Gemini response
    mock_gemini.return_value = "This is a mock AI response about elections."
    
    response = client.post('/api/chat', json={'message': 'How do I vote?'})
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['response'] == "This is a mock AI response about elections."
    mock_gemini.assert_called_once_with('How do I vote?', [])

@patch('app.get_gemini_response')
def test_chat_api_exception(mock_gemini, client):
    """Test chat API when the Gemini service throws an error."""
    mock_gemini.side_effect = Exception("API Server Down")
    
    response = client.post('/api/chat', json={'message': 'Hello'})
    assert response.status_code == 500
    
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'trouble processing' in data['error']
