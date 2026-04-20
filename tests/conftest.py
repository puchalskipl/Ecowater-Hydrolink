# -*- coding: utf-8 -*-
import asyncio
import contextlib
import os
import sys
from unittest.mock import AsyncMock, Mock, patch
import pytest
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from pytest_socket import disable_socket, enable_socket


if sys.platform == "win32":
    # On Windows, ProactorEventLoop.self_pipe goes through socket.socket() (no native
    # socketpair), so any disable_socket() call breaks every pytest-asyncio test.
    # pytest-homeassistant-custom-component disables sockets for every test in its
    # pytest_runtest_setup hook, which we cannot reorder reliably. Neuter it here.
    # Tests use mocks, so allowing real sockets is harmless. CI runs on Linux.
    import pytest_socket
    pytest_socket.disable_socket = lambda *args, **kwargs: None


@pytest.fixture(autouse=True)
def disable_socket_for_tests():
    """Disable socket usage for most tests (Linux/macOS only)."""
    if sys.platform == "win32":
        return True
    with contextlib.suppress(Exception):
        disable_socket()
    return True


class MockEventLoop(asyncio.AbstractEventLoop):
    """A mock event loop for testing."""

    def __init__(self):
        self.run_in_executor = AsyncMock()
        self.create_task = Mock()
        self.set_debug = Mock()
        self.run_until_complete = Mock()
        self.close = Mock()

    def get_debug(self):
        return False

    def create_future(self):
        fut = asyncio.Future()
        fut.set_result(None)
        return fut
    
    def call_soon(self, callback, *args, context=None):
        callback(*args)
        return None

    def is_running(self):
        return True

    def is_closed(self):
        return False

    def stop(self):
        pass

    def call_exception_handler(self, context):
        pass

    def default_exception_handler(self, context):
        pass

    def call_soon_threadsafe(self, callback, *args):
        return self.call_soon(callback, *args)

    def get_exception_handler(self):
        return None

    def set_exception_handler(self, handler):
        pass

@pytest.fixture
def mock_event_loop():
    """Create a mock event loop for use in tests."""
    loop = MockEventLoop()
    asyncio.set_event_loop(loop)
    return loop

@pytest.fixture
def hass(mock_event_loop):
    """Create mock Home Assistant instance for testing."""
    hass = Mock(spec=HomeAssistant)
    hass.config = Mock()
    hass.config.config_dir = "/test/config"
    hass.data = {
        "integrations": {},
        "device_registry": {},
        "entity_registry": {},
    }
    hass.config.components = set()
    hass.services = Mock()
    hass.services.async_register = AsyncMock()
    hass.async_add_executor_job = AsyncMock()
    hass.config_entries = Mock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_forward_entry_unload = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries.async_entries = AsyncMock(return_value=[])
    hass.config_entries.async_flow_progress = AsyncMock(return_value=[])
    hass.loop = mock_event_loop
    
    return hass