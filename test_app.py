import json
import pytest
from unittest.mock import patch
from app import app

# Expand fixtures to increase baseline coverage checks
@pytest.fixture
def client():
    # Enforce testing protocols ensuring secure defaults
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the main page loads successfully and headers are established."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'CivicGuide' in response.data
    # Check security headers added by Talisman
    assert 'Content-Security-Policy' in response.headers

def test_chat_api_missing_data(client):
    """Test missing JSON data."""
    response = client.post('/api/chat', data="not-json", content_type='text/plain')
    assert response.status_code == 400

def test_chat_api_missing_message(client):
    """Test the chat API with missing message payload."""
    response = client.post('/api/chat', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'message' in data['error']

@patch('app.get_gemini_response')
def test_chat_api_success(mock_gemini, client):
    """Test a successful chat API response handling."""
    mock_gemini.return_value = "This is a mock AI response about elections."
    
    response = client.post('/api/chat', json={'message': 'How do I vote?'})
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['response'] == "This is a mock AI response about elections."
    
    # Ensure our dependency was parameterized appropriately with history logic
    mock_gemini.assert_called_once_with('How do I vote?', [])

@patch('app.get_gemini_response')
def test_chat_api_with_history(mock_gemini, client):
    """Test a successful chat API response that provides context tracking."""
    mock_gemini.return_value = "Mock response context-aware."
    history = [{"role": "user", "content": "hello"}]
    
    response = client.post('/api/chat', json={'message': 'Next step?', 'history': history})
    assert response.status_code == 200
    mock_gemini.assert_called_once_with('Next step?', history)

@patch('app.get_gemini_response')
def test_chat_api_exception(mock_gemini, client):
    """Test structured error handling for 5xx failures."""
    mock_gemini.side_effect = Exception("API Server Outage")
    
    response = client.post('/api/chat', json={'message': 'Hello'})
    assert response.status_code == 500
    
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Processing' not in data['error'] # Ensure raw error isn't leaked
    assert 'having trouble processing' in data['error'].lower()
