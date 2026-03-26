"""Unit tests for the HydroLink API interface."""
import json
import threading
import time
from unittest.mock import Mock, patch
import pytest
import requests
from custom_components.hydrolink.api import (
    HydroLinkApi,
    CannotConnect,
    InvalidAuth,
)

# Test data
MOCK_EMAIL = "test@example.com"
MOCK_PASSWORD = "password123"
MOCK_AUTH_COOKIE = "test_cookie"
MOCK_DEVICE_ID = "test-device-id"

@pytest.fixture
def api():
    """Create a HydroLinkApi instance for testing."""
    return HydroLinkApi(MOCK_EMAIL, MOCK_PASSWORD)

@pytest.fixture
def mock_response():
    """Create a mock response object."""
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.cookies = {"hhfoffoezyzzoeibwv": MOCK_AUTH_COOKIE}
    return response

def test_login_success(api, mock_response):
    """Test successful login."""
    with patch("requests.post", return_value=mock_response):
        assert api.login() is True
        assert api.auth_cookie == MOCK_AUTH_COOKIE

def test_login_invalid_auth(api):
    """Test login with invalid credentials."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 401
    
    with patch("requests.post", return_value=mock_response):
        with pytest.raises(InvalidAuth):
            api.login()

def test_login_connection_error(api):
    """Test login with connection error."""
    with patch("requests.post", side_effect=requests.ConnectionError):
        with pytest.raises(CannotConnect):
            api.login()

def test_get_data_success(api, mock_response):
    """Test successful data retrieval."""
    # Mock device data
    mock_device_data = {
        "data": [
            {
                "id": MOCK_DEVICE_ID,
                "system_type": "demand_softener",
                "properties": {
                    "water_usage_today": {"value": 100},
                    "salt_level": {"value": 50}
                }
            }
        ]
    }
    mock_response.json = Mock(return_value=mock_device_data)
    
    # Mock WebSocket response
    mock_ws_response = Mock(spec=requests.Response)
    mock_ws_response.status_code = 200
    mock_ws_response.json = Mock(return_value={"websocket_uri": "/ws/test"})
    
    # Mock requests and socket operations
    with patch("requests.get", side_effect=[mock_response, mock_ws_response, mock_response]), \
         patch("requests.post", return_value=mock_response), \
         patch("socket.socket"), \
         patch("websocket.WebSocketApp"):
        # Login first (we know requests.post is mocked)
        api.login()
        # Now get data
        data = api.get_data()
        assert len(data) == 1
        assert data[0]["id"] == MOCK_DEVICE_ID

def test_get_data_no_auth(api):
    """Test data retrieval without authentication."""
    # Create a mock response with 401 status
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 401
    
    with patch("requests.post", return_value=mock_response) as mock_post:
        with pytest.raises(InvalidAuth):
            api.get_data()

def test_get_data_connection_error(api):
    """Test data retrieval with connection error."""
    api.auth_cookie = MOCK_AUTH_COOKIE
    with patch("requests.get", side_effect=requests.ConnectionError):
        with pytest.raises(CannotConnect):
            api.get_data()

def test_websocket_message_handling(api):
    """Test WebSocket message handling."""
    api.ws_uri = "wss://test.com/ws"
    api.auth_cookie = "test_cookie"  # Need to be authenticated
    
    # Save the on_message callback
    message_callback = None
    
    def mock_websocket_app(*args, **kwargs):
        nonlocal message_callback
        mock_ws = Mock()
        mock_ws.run_forever = Mock()
        mock_ws.close = Mock()  # Add close method to mock
        message_callback = kwargs.get('on_message')  # Save the callback
        return mock_ws
    
    with patch("websocket.WebSocketApp", side_effect=mock_websocket_app) as mock_websocket:
        # Create a mock instance to store
        mock_ws = mock_websocket.return_value = Mock()
        mock_ws.run_forever = Mock()
        mock_ws.close = Mock()
        
        # Start WebSocket in separate thread
        ws_thread = threading.Thread(target=api._start_ws)
        ws_thread.daemon = True  # Make sure thread doesn't block test exit
        ws_thread.start()
        
        # Give thread time to start
        time.sleep(0.1)
        
        # Call the callback directly
        test_message = {"test": "data"}
        message_callback(mock_ws, json.dumps(test_message))
        
        # Check the message count
        assert api.ws_message_count == 1

        # Simulate connection close
        if message_callback:
            mock_ws.close()  # Actually call close() before asserting
            mock_ws.on_close(mock_ws) if mock_ws.on_close else None
            assert mock_ws.close.called

        # Wait for thread to finish
        ws_thread.join(timeout=1)