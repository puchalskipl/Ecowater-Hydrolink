"""Unit tests for the HydroLink coordinator."""
from unittest.mock import AsyncMock, Mock, patch
import pytest
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.hydrolink.coordinator import HydroLinkDataUpdateCoordinator
from custom_components.hydrolink.const import DOMAIN
from custom_components.hydrolink.api import HydroLinkApi, CannotConnect, InvalidAuth

# Test data
MOCK_CONFIG = {
    "email": "test@example.com",
    "password": "password123",
    "region": "hydrolinkhome_eu",
}

MOCK_DEVICE_DATA = {
    "deviceId": "test_device_id",
    "deviceName": "Test Water Softener",
    "currentWaterFlow": 1.5,
    "saltLevel": 75.5,
    "onlineStatus": True
}

@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Create a mock config entry."""
    # Handle different Home Assistant versions that may or may not require discovery_keys
    try:
        return ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title="HydroLink Test",
            data=MOCK_CONFIG,
            source="user",
            options={},
            unique_id="test@example.com",
            discovery_keys=None
        )
    except TypeError:
        # Fallback for older HA versions that don't support discovery_keys
        return ConfigEntry(
            version=1,
            minor_version=1,
            domain=DOMAIN,
            title="HydroLink Test",
            data=MOCK_CONFIG,
            source="user",
            options={},
            unique_id="test@example.com"
        )

@pytest.fixture
def mock_api():
    """Create a mock API."""
    api = Mock(spec=HydroLinkApi)
    api.login = Mock(return_value=True)
    api.get_data = Mock(return_value=[MOCK_DEVICE_DATA])
    return api

@pytest.mark.asyncio
async def test_coordinator_initialization(hass: HomeAssistant, mock_config_entry: ConfigEntry):
    """Test coordinator initialization."""
    coordinator = HydroLinkDataUpdateCoordinator(hass, mock_config_entry)
    
    assert coordinator.hass == hass
    assert coordinator.config_entry == mock_config_entry
    assert coordinator.update_interval == timedelta(minutes=5)
    assert coordinator.api.email == MOCK_CONFIG["email"]
    assert coordinator.api.password == MOCK_CONFIG["password"]


@pytest.mark.asyncio
async def test_coordinator_update_success(hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_api):
    """Test successful coordinator data update."""
    coordinator = HydroLinkDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.api = mock_api
    
    # Mock the async executor job
    async def mock_executor_job(func):
        return func()
    
    hass.async_add_executor_job = mock_executor_job
    
    data = await coordinator._async_update_data()
    
    assert len(data) == 1
    assert data[0]["id"] == "test_device_id"
    mock_api.login.assert_called_once()
    mock_api.get_data.assert_called_once()


@pytest.mark.asyncio
async def test_coordinator_update_auth_failure(hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_api):
    """Test coordinator data update with authentication failure."""
    coordinator = HydroLinkDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.api = mock_api
    
    # Mock login failure
    mock_api.login.side_effect = InvalidAuth("Invalid credentials")
    
    # Mock the async executor job
    async def mock_executor_job(func):
        return func()
    
    hass.async_add_executor_job = mock_executor_job
    
    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_update_connection_failure(hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_api):
    """Test coordinator data update with connection failure."""
    coordinator = HydroLinkDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.api = mock_api
    
    # Mock connection failure
    mock_api.login.side_effect = CannotConnect("Network error")
    
    # Mock the async executor job
    async def mock_executor_job(func):
        return func()
    
    hass.async_add_executor_job = mock_executor_job
    
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_update_generic_exception(hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_api):
    """Test coordinator data update with generic exception."""
    coordinator = HydroLinkDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.api = mock_api
    
    # Mock generic exception
    mock_api.login.side_effect = Exception("Unexpected error")
    
    # Mock the async executor job
    async def mock_executor_job(func):
        return func()
    
    hass.async_add_executor_job = mock_executor_job
    
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_get_data_failure(hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_api):
    """Test coordinator when get_data fails after successful login."""
    coordinator = HydroLinkDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.api = mock_api
    
    # Login succeeds but get_data fails
    mock_api.login.return_value = True
    mock_api.get_data.side_effect = CannotConnect("API error")
    
    # Mock the async executor job
    async def mock_executor_job(func):
        return func()
    
    hass.async_add_executor_job = mock_executor_job
    
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_empty_devices_list(hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_api):
    """Test coordinator when API returns empty devices list."""
    coordinator = HydroLinkDataUpdateCoordinator(hass, mock_config_entry)
    coordinator.api = mock_api
    
    # Mock empty devices list
    mock_api.get_data.return_value = []
    
    # Mock the async executor job
    async def mock_executor_job(func):
        return func()
    
    hass.async_add_executor_job = mock_executor_job
    
    data = await coordinator._async_update_data()
    
    assert data == []
    mock_api.login.assert_called_once()
    mock_api.get_data.assert_called_once()