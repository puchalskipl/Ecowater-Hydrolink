# -*- coding: utf-8 -*-
"""Test helpers."""
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.core import HomeAssistant


def create_mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)

    async def async_exec_with_exc(func, *args, **kwargs):
        return func(*args, **kwargs)
    hass.async_add_executor_job = async_exec_with_exc

    config_entries = Mock()
    config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    config_entries.async_forward_entry_unload = AsyncMock(return_value=True)
    config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries = config_entries
    hass.data = {}
    hass.config = Mock()
    hass.config.components = set()
    hass.services = Mock()
    hass.services.async_register = AsyncMock()

    return hass
