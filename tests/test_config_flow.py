"""Test the config flow."""
from contextlib import contextmanager
from unittest.mock import AsyncMock, Mock, PropertyMock, patch
import pytest
import voluptuous as vol
from homeassistant import config_entries, data_entry_flow
from custom_components.hydrolink.const import (
    DOMAIN,
    CONF_REGION,
    CONF_SCAN_INTERVAL,
    REGION_COM,
    REGION_EU,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    MAX_SCAN_INTERVAL_MINUTES,
)
from custom_components.hydrolink.config_flow import ConfigFlow, OptionsFlowHandler
from custom_components.hydrolink.api import CannotConnect, InvalidAuth
from tests.helpers import create_mock_hass

# Test data
MOCK_EMAIL = "test@example.com"
MOCK_PASSWORD = "password123"

def setup_mock_flow():
    """Set up a config flow with mocked hass instance."""
    # Create and initialize the flow with a mocked hass instance
    flow = ConfigFlow()
    flow.hass = create_mock_hass()

    # Mock the required async methods
    mock_async_entries = AsyncMock(return_value=[])
    mock_async_progress = AsyncMock(return_value=[])
    mock_set_unique_id = AsyncMock()

    mock_entries = Mock()
    mock_entries.async_entries = mock_async_entries
    mock_entries.async_flow_progress = mock_async_progress

    flow.hass.config_entries = mock_entries
    flow.async_set_unique_id = mock_set_unique_id

    return flow

@pytest.mark.asyncio
async def test_form():
    """Test showing the region selection form."""
    flow = setup_mock_flow()

    result = await flow.async_step_user()
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

@pytest.mark.asyncio
async def test_region_selection_proceeds_to_credentials():
    """Test that selecting a region proceeds to credentials step."""
    flow = setup_mock_flow()

    result = await flow.async_step_user({CONF_REGION: REGION_COM})
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "credentials"

@pytest.mark.asyncio
async def test_user_input_validation():
    """Test input validation."""
    flow = setup_mock_flow()

    # Select region first
    await flow.async_step_user({CONF_REGION: REGION_COM})

    # Test with empty email
    result = await flow.async_step_credentials({"email": "", "password": MOCK_PASSWORD})
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}

    # Test with empty password
    result = await flow.async_step_credentials({"email": MOCK_EMAIL, "password": ""})
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}

@pytest.mark.asyncio
async def test_successful_config_flow():
    """Test a successful config flow."""
    flow = setup_mock_flow()

    # Mock async_set_unique_id to return None
    mock_set_unique_id = AsyncMock(return_value=None)
    flow.async_set_unique_id = mock_set_unique_id

    # Mock _abort_if_unique_id_configured to do nothing
    flow._abort_if_unique_id_configured = Mock()

    with patch(
        "custom_components.hydrolink.api.HydroLinkApi.login",
        return_value=True,
    ):
        # First select region
        result = await flow.async_step_user({CONF_REGION: REGION_COM})
        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["step_id"] == "credentials"

        # Now submit credentials
        result = await flow.async_step_credentials({
            "email": MOCK_EMAIL,
            "password": MOCK_PASSWORD,
        })

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == MOCK_EMAIL
    assert result["data"] == {
        "email": MOCK_EMAIL,
        "password": MOCK_PASSWORD,
        CONF_REGION: REGION_COM,
    }

@pytest.mark.asyncio
async def test_successful_config_flow_europe():
    """Test a successful config flow with Europe region."""
    flow = setup_mock_flow()

    mock_set_unique_id = AsyncMock(return_value=None)
    flow.async_set_unique_id = mock_set_unique_id
    flow._abort_if_unique_id_configured = Mock()

    with patch(
        "custom_components.hydrolink.api.HydroLinkApi.login",
        return_value=True,
    ):
        # Select Europe region
        result = await flow.async_step_user({CONF_REGION: REGION_EU})
        assert result["type"] == data_entry_flow.FlowResultType.FORM

        # Submit credentials
        result = await flow.async_step_credentials({
            "email": MOCK_EMAIL,
            "password": MOCK_PASSWORD,
        })

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_REGION] == REGION_EU

@pytest.mark.asyncio
async def test_failed_config_flow_invalid_auth():
    """Test a failed config flow due to invalid auth."""
    flow = setup_mock_flow()

    # Select region first
    await flow.async_step_user({CONF_REGION: REGION_COM})

    # Now submit invalid credentials
    with patch(
        "custom_components.hydrolink.api.HydroLinkApi.login",
        side_effect=InvalidAuth,
    ):
        result = await flow.async_step_credentials({
            "email": MOCK_EMAIL,
            "password": MOCK_PASSWORD,
        })

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}

@pytest.mark.asyncio
async def test_failed_config_flow_cannot_connect():
    """Test a failed config flow due to connection error."""
    flow = setup_mock_flow()

    # Select region first
    await flow.async_step_user({CONF_REGION: REGION_COM})

    # Now submit with connection error
    with patch(
        "custom_components.hydrolink.api.HydroLinkApi.login",
        side_effect=CannotConnect,
    ):
        result = await flow.async_step_credentials({
            "email": MOCK_EMAIL,
            "password": MOCK_PASSWORD,
        })

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


# ---------- Options flow ----------

def _make_entry(options=None):
    entry = Mock()
    entry.options = options or {}
    return entry


@contextmanager
def _options_handler(entry):
    """Construct an OptionsFlowHandler with a fake config_entry.

    HA 2024.11+ exposes `OptionsFlow.config_entry` as a read-only property bound
    to the entry passed to `async_get_options_flow`. Older HA versions don't
    have the attribute on the class at all. `create=True` covers both cases.
    """
    handler = OptionsFlowHandler()
    with patch.object(
        OptionsFlowHandler,
        "config_entry",
        new_callable=PropertyMock,
        return_value=entry,
        create=True,
    ):
        yield handler


def test_async_get_options_flow_returns_handler():
    handler = ConfigFlow.async_get_options_flow(_make_entry())
    assert isinstance(handler, OptionsFlowHandler)


@pytest.mark.asyncio
async def test_options_flow_shows_form_with_current_value():
    entry = _make_entry({CONF_SCAN_INTERVAL: 12})
    with _options_handler(entry) as handler:
        result = await handler.async_step_init()

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "init"
    schema_keys = {k.schema: k.default() for k in result["data_schema"].schema}
    assert schema_keys[CONF_SCAN_INTERVAL] == 12


@pytest.mark.asyncio
async def test_options_flow_defaults_to_constant_when_not_set():
    with _options_handler(_make_entry()) as handler:
        result = await handler.async_step_init()

    schema_keys = {k.schema: k.default() for k in result["data_schema"].schema}
    assert schema_keys[CONF_SCAN_INTERVAL] == DEFAULT_SCAN_INTERVAL_MINUTES


@pytest.mark.asyncio
async def test_options_flow_creates_entry_on_submit():
    with _options_handler(_make_entry()) as handler:
        result = await handler.async_step_init({CONF_SCAN_INTERVAL: 10})

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_SCAN_INTERVAL: 10}


@pytest.mark.asyncio
async def test_options_flow_rejects_out_of_range_via_schema():
    """Voluptuous schema must reject values outside [MIN, MAX]."""
    with _options_handler(_make_entry()) as handler:
        result = await handler.async_step_init()
    schema = result["data_schema"]

    with pytest.raises(vol.Invalid):
        schema({CONF_SCAN_INTERVAL: MAX_SCAN_INTERVAL_MINUTES + 1})
    with pytest.raises(vol.Invalid):
        schema({CONF_SCAN_INTERVAL: 0})


@pytest.mark.asyncio
async def test_options_flow_coerces_string_to_int():
    """Schema accepts string-typed numeric input from the UI."""
    with _options_handler(_make_entry()) as handler:
        result = await handler.async_step_init()
    schema = result["data_schema"]

    validated = schema({CONF_SCAN_INTERVAL: "15"})
    assert validated[CONF_SCAN_INTERVAL] == 15


def test_options_flow_handler_does_not_assign_config_entry():
    """Regression: HA 2024.11+ makes `config_entry` a read-only property, so
    assigning it from __init__ raises AttributeError and breaks Configure with
    a 500. Source-level check works across HA versions."""
    import inspect
    src = inspect.getsource(OptionsFlowHandler)
    assert "self.config_entry =" not in src, (
        "OptionsFlowHandler must not assign self.config_entry — "
        "it crashes Configure on HA 2024.11+"
    )