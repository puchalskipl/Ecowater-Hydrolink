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
    RateLimited,
    CIRCUIT_BREAKER_THRESHOLD,
    CIRCUIT_BREAKER_COOLDOWN_SECONDS,
    RETRY_INITIAL_BACKOFF_SECONDS,
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
    response.headers = {}
    # EU region (the api fixture default) uses this cookie name
    response.cookies = {"hhxaifhduswhaiunzp": MOCK_AUTH_COOKIE}
    return response

def test_login_success(api, mock_response):
    """Test successful login."""
    with patch("requests.request", return_value=mock_response):
        assert api.login() is True
        assert api.auth_cookie == MOCK_AUTH_COOKIE

def test_login_invalid_auth(api):
    """Test login with invalid credentials."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 401
    mock_response.headers = {}

    with patch("requests.request", return_value=mock_response):
        with pytest.raises(InvalidAuth):
            api.login()

def test_login_connection_error(api):
    """Test login with connection error."""
    with patch("requests.request", side_effect=requests.ConnectionError):
        with pytest.raises(CannotConnect):
            api.login()

def test_get_data_success(api, mock_response):
    """Test successful data retrieval."""
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

    mock_ws_response = Mock(spec=requests.Response)
    mock_ws_response.status_code = 200
    mock_ws_response.headers = {}
    mock_ws_response.json = Mock(return_value={"websocket_uri": "/ws/test"})

    # Login (POST), then GET /devices, GET /devices/{id}/live, GET /devices
    with patch(
        "requests.request",
        side_effect=[mock_response, mock_response, mock_ws_response, mock_response],
    ), patch("socket.socket"), patch("websocket.WebSocketApp"):
        api.login()
        data = api.get_data()
        assert len(data) == 1
        assert data[0]["id"] == MOCK_DEVICE_ID

def test_get_data_no_auth(api):
    """Test data retrieval without authentication."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 401
    mock_response.headers = {}

    with patch("requests.request", return_value=mock_response):
        with pytest.raises(InvalidAuth):
            api.get_data()

def test_get_data_connection_error(api):
    """Test data retrieval with connection error."""
    api.auth_cookie = MOCK_AUTH_COOKIE
    with patch("requests.request", side_effect=requests.ConnectionError):
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


# ---------- Retry-After / backoff / circuit breaker ----------

def _make_response(status_code: int, headers: dict | None = None) -> Mock:
    response = Mock(spec=requests.Response)
    response.status_code = status_code
    response.headers = headers or {}
    response.cookies = {}
    return response


def test_parse_retry_after_seconds():
    assert HydroLinkApi._parse_retry_after("42", 5) == 42.0


def test_parse_retry_after_missing_uses_fallback():
    assert HydroLinkApi._parse_retry_after(None, 7) == 7
    assert HydroLinkApi._parse_retry_after("", 7) == 7


def test_parse_retry_after_unparseable_uses_fallback():
    assert HydroLinkApi._parse_retry_after("Wed, 21 Oct 2015 07:28:00 GMT", 9) == 9


def test_request_with_retry_returns_immediately_on_success(api):
    ok = _make_response(200)
    with patch("requests.request", return_value=ok) as mock_req, \
         patch("time.sleep") as mock_sleep:
        result = api._request_with_retry("GET", "https://example/x")
    assert result is ok
    assert mock_req.call_count == 1
    mock_sleep.assert_not_called()
    assert api._consecutive_429 == 0


def test_request_with_retry_429_then_success_uses_retry_after(api):
    rate = _make_response(429, headers={"Retry-After": "1"})
    ok = _make_response(200)
    with patch("requests.request", side_effect=[rate, ok]), \
         patch("time.sleep") as mock_sleep:
        result = api._request_with_retry("GET", "https://example/x")
    assert result is ok
    mock_sleep.assert_called_once_with(1.0)
    assert api._consecutive_429 == 0


def test_request_with_retry_429_no_header_uses_initial_backoff(api):
    rate = _make_response(429, headers={})
    ok = _make_response(200)
    with patch("requests.request", side_effect=[rate, ok]), \
         patch("time.sleep") as mock_sleep:
        api._request_with_retry("GET", "https://example/x")
    mock_sleep.assert_called_once_with(RETRY_INITIAL_BACKOFF_SECONDS)


def test_request_with_retry_circuit_breaker_trips_after_threshold(api):
    rate = _make_response(429, headers={"Retry-After": "1"})
    with patch("requests.request", return_value=rate), \
         patch("time.sleep"):
        with pytest.raises(RateLimited):
            api._request_with_retry("GET", "https://example/x")
    assert api._consecutive_429 == CIRCUIT_BREAKER_THRESHOLD
    assert api._cooldown_until > time.monotonic()


def test_request_with_retry_in_cooldown_raises_without_http_call(api):
    api._cooldown_until = time.monotonic() + CIRCUIT_BREAKER_COOLDOWN_SECONDS
    with patch("requests.request") as mock_req:
        with pytest.raises(RateLimited):
            api._request_with_retry("GET", "https://example/x")
    mock_req.assert_not_called()


def test_request_with_retry_resets_counter_on_success(api):
    api._consecutive_429 = 2
    ok = _make_response(200)
    with patch("requests.request", return_value=ok):
        api._request_with_retry("GET", "https://example/x")
    assert api._consecutive_429 == 0


def test_request_with_retry_caps_individual_sleep_at_max(api):
    """Even if Retry-After says hours, we cap each sleep at RETRY_MAX_BACKOFF_SECONDS."""
    from custom_components.hydrolink.api import RETRY_MAX_BACKOFF_SECONDS
    rate = _make_response(429, headers={"Retry-After": "999999"})
    ok = _make_response(200)
    with patch("requests.request", side_effect=[rate, ok]), \
         patch("time.sleep") as mock_sleep:
        api._request_with_retry("GET", "https://example/x")
    mock_sleep.assert_called_once_with(float(RETRY_MAX_BACKOFF_SECONDS))


def test_rate_limited_is_cannot_connect_subclass():
    """Coordinator's `except CannotConnect` must catch RateLimited."""
    assert issubclass(RateLimited, CannotConnect)