"""Unit tests for the HydroLink sensor platform."""
from unittest.mock import Mock, patch
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfVolume,
    UnitOfTime,
    UnitOfMass,
)
from custom_components.hydrolink.sensor import (
    HydroLinkSensor,
    async_setup_entry,
    DEFAULT_ENABLED_SENSORS,
    SENSOR_DESCRIPTIONS,
)

# Test data
MOCK_DEVICE_ID = "test-device-id"
MOCK_DEVICE_NAME = "Test Device"
MOCK_PROPERTY = "water_usage_today"
MOCK_VALUE = 100

@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = Mock()
    coordinator.data = [
        {
            "id": MOCK_DEVICE_ID,
            "properties": {
                MOCK_PROPERTY: {"value": MOCK_VALUE}
            }
        }
    ]
    return coordinator

@pytest.fixture
def sensor(mock_coordinator):
    """Create a HydroLinkSensor instance for testing."""
    return HydroLinkSensor(
        mock_coordinator,
        MOCK_DEVICE_ID,
        MOCK_PROPERTY,
        MOCK_DEVICE_NAME,
        {"value": MOCK_VALUE},
    )

def test_sensor_creation(sensor):
    """Test sensor object creation."""
    assert sensor._device_id == MOCK_DEVICE_ID
    assert sensor._property_name == MOCK_PROPERTY
    assert sensor._device_name == MOCK_DEVICE_NAME

def test_sensor_native_value(sensor):
    """Test sensor value retrieval."""
    assert sensor.native_value == MOCK_VALUE

def test_sensor_tenths_conversion():
    """Test that sensors ending in _tenths are divided by 10."""
    coordinator = Mock()
    coordinator.data = [
        {
            "id": MOCK_DEVICE_ID,
            "properties": {
                "salt_level_tenths": {"value": 750},
                "iron_level_tenths_ppm": {"value": 25},
                "tlc_avg_temp_tenths_c": {"value": 310},
            }
        }
    ]

    salt_sensor = HydroLinkSensor(coordinator, MOCK_DEVICE_ID, "salt_level_tenths", MOCK_DEVICE_NAME, {"value": 750})
    assert salt_sensor.native_value == 75.0

    iron_sensor = HydroLinkSensor(coordinator, MOCK_DEVICE_ID, "iron_level_tenths_ppm", MOCK_DEVICE_NAME, {"value": 25})
    assert iron_sensor.native_value == 2.5

    temp_sensor = HydroLinkSensor(coordinator, MOCK_DEVICE_ID, "tlc_avg_temp_tenths_c", MOCK_DEVICE_NAME, {"value": 310})
    assert temp_sensor.native_value == 31.0

def test_sensor_capacity_remaining_conversion():
    """Test that capacity_remaining_percent is divided by 10."""
    coordinator = Mock()
    coordinator.data = [
        {
            "id": MOCK_DEVICE_ID,
            "properties": {
                "capacity_remaining_percent": {"value": 850},
            }
        }
    ]

    sensor = HydroLinkSensor(coordinator, MOCK_DEVICE_ID, "capacity_remaining_percent", MOCK_DEVICE_NAME, {"value": 850})
    assert sensor.native_value == 85.0

def test_sensor_salt_values_conversion():
    """Test that salt values are divided by 1000 (API sends in thousandths)."""
    coordinator = Mock()
    coordinator.data = [
        {
            "id": MOCK_DEVICE_ID,
            "properties": {
                "avg_salt_per_regen_lbs": {"value": 6670},
                "total_salt_use_lbs": {"value": 667000},
            }
        }
    ]

    avg_sensor = HydroLinkSensor(coordinator, MOCK_DEVICE_ID, "avg_salt_per_regen_lbs", MOCK_DEVICE_NAME, {"value": 6670})
    assert avg_sensor.native_value == 6.67

    total_sensor = HydroLinkSensor(coordinator, MOCK_DEVICE_ID, "total_salt_use_lbs", MOCK_DEVICE_NAME, {"value": 667000})
    assert total_sensor.native_value == 667.0

def test_sensor_metric_conversion_liters():
    """Test that EU region sensors use converted_value in liters."""
    coordinator = Mock()
    coordinator.data = [
        {
            "id": MOCK_DEVICE_ID,
            "properties": {
                "gallons_used_today": {
                    "value": 50,
                    "converted_value": 189,
                    "converted_units": "Liters",
                },
            }
        }
    ]

    prop_info = {"value": 50, "converted_value": 189, "converted_units": "Liters"}
    sensor = HydroLinkSensor(coordinator, MOCK_DEVICE_ID, "gallons_used_today", MOCK_DEVICE_NAME, prop_info)
    assert sensor.native_value == 189
    assert sensor._attr_native_unit_of_measurement == UnitOfVolume.LITERS

def test_sensor_metric_conversion_kilograms():
    """Test that EU region salt sensors use converted_value in kilograms."""
    coordinator = Mock()
    coordinator.data = [
        {
            "id": MOCK_DEVICE_ID,
            "properties": {
                "avg_salt_per_regen_lbs": {
                    "value": 17822,
                    "converted_value": 8084,
                    "converted_units": "kilograms",
                },
            }
        }
    ]

    prop_info = {"value": 17822, "converted_value": 8084, "converted_units": "kilograms"}
    sensor = HydroLinkSensor(coordinator, MOCK_DEVICE_ID, "avg_salt_per_regen_lbs", MOCK_DEVICE_NAME, prop_info)
    # converted_value 8084 still gets /1000 scaling
    assert sensor.native_value == 8.084
    assert sensor._attr_native_unit_of_measurement == UnitOfMass.KILOGRAMS

def test_sensor_metric_conversion_liters_per_min():
    """Test that EU region flow sensors use converted_value in L/min."""
    coordinator = Mock()
    coordinator.data = [
        {
            "id": MOCK_DEVICE_ID,
            "properties": {
                "current_water_flow_gpm": {
                    "value": 5.0,
                    "converted_value": 18.927,
                    "converted_units": "liters/min",
                },
            }
        }
    ]

    prop_info = {"value": 5.0, "converted_value": 18.927, "converted_units": "liters/min"}
    sensor = HydroLinkSensor(coordinator, MOCK_DEVICE_ID, "current_water_flow_gpm", MOCK_DEVICE_NAME, prop_info)
    assert sensor.native_value == 18.927
    assert sensor._attr_native_unit_of_measurement == "L/min"

def test_sensor_no_conversion_without_converted_value():
    """Test that sensors without converted_value use raw value (US region)."""
    coordinator = Mock()
    coordinator.data = [
        {
            "id": MOCK_DEVICE_ID,
            "properties": {
                "gallons_used_today": {"value": 50},
            }
        }
    ]

    prop_info = {"value": 50}
    sensor = HydroLinkSensor(coordinator, MOCK_DEVICE_ID, "gallons_used_today", MOCK_DEVICE_NAME, prop_info)
    assert sensor.native_value == 50
    assert sensor._attr_native_unit_of_measurement == UnitOfVolume.GALLONS

def test_sensor_attributes(sensor):
    """Test sensor attributes from descriptions."""
    description = SENSOR_DESCRIPTIONS.get(MOCK_PROPERTY)
    if description:
        assert sensor._attr_native_unit_of_measurement == description.get("unit")
        assert sensor._attr_device_class == description.get("device_class")
        assert sensor._attr_state_class == description.get("state_class")
        assert sensor._attr_icon == description.get("icon")

def test_sensor_unique_id(sensor):
    """Test sensor unique ID generation."""
    assert sensor._attr_unique_id == f"hydrolink_{MOCK_DEVICE_ID}_{MOCK_PROPERTY}"

def test_sensor_device_info(sensor):
    """Test sensor device info."""
    device_info = sensor.device_info
    assert device_info["identifiers"] == {("hydrolink", MOCK_DEVICE_ID)}
    assert device_info["name"] == MOCK_DEVICE_NAME
    assert device_info["manufacturer"] == "EcoWater"

def test_sensor_default_enabled(sensor):
    """Test sensor default enabled state."""
    assert sensor._attr_entity_registry_enabled_default == (
        sensor._property_name in DEFAULT_ENABLED_SENSORS
    )

@pytest.mark.asyncio
async def test_async_setup_entry(hass: HomeAssistant):
    """Test platform setup."""
    mock_entry = Mock()
    mock_coordinator = Mock()
    mock_coordinator.data = [
        {
            "id": MOCK_DEVICE_ID,
            "system_type": "demand_softener",
            "nickname": MOCK_DEVICE_NAME,
            "properties": {
                "water_usage_today": {"value": 100},
                "salt_level": {"value": 50}
            }
        }
    ]

    # Set up the hass mock properly
    hass.config = Mock()
    hass.config.config_dir = "/test/config"
    hass.data = {"hydrolink": {mock_entry.entry_id: mock_coordinator}}

    # Create the async_add_entities mock
    async_add_entities = Mock()
    await async_setup_entry(hass, mock_entry, async_add_entities)

    # Verify entities were created and added
    assert async_add_entities.called
    entities = async_add_entities.call_args[0][0]
    assert len(entities) == 2  # Two properties in mock data