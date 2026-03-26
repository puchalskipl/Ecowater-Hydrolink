# -*- coding: utf-8 -*-
"""
EcoWater HydroLink Sensor Platform for Home Assistant

Comprehensive sensor platform implementation for monitoring EcoWater HydroLink water
softener devices. Provides 30+ sensors across 8 categories including water usage,
salt management, system performance, regeneration status, and maintenance alerts.

Key Features:
- Real-time water usage and flow monitoring with WebSocket updates
- Comprehensive salt level tracking and efficiency analytics
- System performance metrics and capacity monitoring
- Regeneration status and history tracking
- Proactive alert notifications for maintenance needs
- Device health and connectivity monitoring
- Standardized imperial units (gallons, GPM, pounds, grains)
- Proper Home Assistant entity categorization and device classes
- Automatic sensor discovery - all API properties are exposed as sensors
- Sensors can be enabled/disabled individually in Home Assistant UI

Sensor Categories:
1. Basic System Information - Device status, model, identifiers
2. Water Usage Monitoring - Flow rates, consumption tracking
3. Salt Management - Levels, efficiency, usage patterns
4. System Performance - Capacity, hardness, treatment metrics
5. Regeneration Management - Status, history, scheduling
6. Critical Alerts - Low salt, errors, flow anomalies
7. Signal and Connection - WiFi strength, network status
8. Maintenance Information - Service reminders, operation stats

Author: GrumpyTanker + AI Assistant
Created: June 12, 2025
Updated: October 10, 2025

Version History:
- 1.3.0 (2026-03-26) - puchalskipl
  * Added automatic metric unit conversion for EU region
  * Sensors use converted_value from API when available (Liters, kg, L/min)
  * Added API_UNIT_MAP for mapping API units to Home Assistant constants
  * US region behavior unchanged (imperial units)

- 1.2.2 (2025-10-10)
  * Fixed critical sensor scaling issues
  * Added 15 new sensor definitions from API
  * Enhanced value conversion logic for tenths, capacity, and salt values
  * Comprehensive test coverage for all conversions
  * Updated documentation with conversion tables

- 1.2.0 (2025-10-03)
  * Enhanced documentation and code comments
  * Improved sensor organization and categorization
  * Version compatibility and testing improvements
  * Code quality standards and linting enhancements
  * Comprehensive error handling patterns

- 1.0.0 (2025-10-03)
  * Production release with 30+ comprehensive sensors
  * Enhanced categorization and entity organization
  * Improved device class assignments and units
  * Real-time WebSocket data integration
  * Comprehensive alert and maintenance tracking

- 0.2.0 (2025-10-02)
  * Added comprehensive sensor categories
  * Standardized imperial unit usage
  * Improved entity categorization and naming
  * Enhanced data validation and error handling

- 0.1.0 (2025-06-12)
  * Initial release with basic sensor support
  * Core integration with HydroLink API
  * Foundation sensor implementations

License: MIT
See LICENSE file in the project root for full license information.
"""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfVolume,
    UnitOfTime,
    UnitOfMass,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

# Mapping from API converted_units strings to Home Assistant unit constants
API_UNIT_MAP = {
    "Liters": UnitOfVolume.LITERS,
    "liters/min": "L/min",
    "kilograms": UnitOfMass.KILOGRAMS,
    "pounds": UnitOfMass.POUNDS,
    "Gallons": UnitOfVolume.GALLONS,
    "Gallon": UnitOfVolume.GALLONS,
    "gpm": "gpm",
    "grains": "grains",
}

# All available sensor categories
SENSOR_CATEGORIES = {
    "BASIC": "Basic system information",
    "WATER": "Water usage and flow metrics",
    "SALT": "Salt level and usage metrics",
    "REGEN": "Regeneration information",
    "PERFORMANCE": "System performance metrics",
    "MAINTENANCE": "Maintenance and service information",
    "ALERTS": "System alerts and warnings",
    "SYSTEM": "System status and configuration"
}

# Set of sensors to be enabled by default
DEFAULT_ENABLED_SENSORS = {
    # Basic Status and System Information
    "_internal_is_online",              # Device online status
    "app_active",                       # Application active status
    "current_time_secs",                # Current device time
    "model_description",                # Model description (EWS ERRC3702R50)
    "nickname",                         # Device nickname

    # Water Usage and Flow Metrics (Imperial)
    "current_water_flow_gpm",           # Current water flow in GPM
    "gallons_used_today",              # Water used today in gallons
    "avg_daily_use_gals",              # Average daily usage in gallons
    "total_outlet_water_gals",         # Total treated water in gallons
    "peak_water_flow_gpm",             # Peak water flow in GPM
    "treated_water_avail_gals",        # Available treated water in gallons

    # Salt Management
    "salt_level_tenths",               # Current salt level in tenths (API value / 10 = %)
    "out_of_salt_estimate_days",       # Days until salt needed
    "avg_salt_per_regen_lbs",          # Average salt per regeneration (lbs)
    "total_salt_use_lbs",              # Total salt used (lbs)

    # System Performance
    "capacity_remaining_percent",       # Remaining capacity percentage
    "operating_capacity_grains",        # Operating capacity in grains
    "hardness_grains",                 # Water hardness in grains
    "rock_removed_since_rech_lbs",     # Hardness removed since recharge (lbs)
    "daily_avg_rock_removed_lbs",      # Daily average hardness removed (lbs)
    "total_rock_removed_lbs",          # Total hardness removed (lbs)

    # Regeneration Status
    "regen_status_enum",               # Current regeneration status
    "days_since_last_regen",           # Days since last regeneration
    "total_regens",                    # Total regeneration count
    "manual_regens",                   # Manual regeneration count
    "regen_time_rem_secs",             # Remaining regeneration time

    # Critical Alerts
    "low_salt_alert",                  # Low salt warning
    "error_code_alert",                # System error alert
    "flow_monitor_alert",              # Flow monitoring alert
    "excessive_water_use_alert",       # High water usage alert
    "floor_leak_detector_alert",       # Leak detection alert
    "service_reminder_alert",          # Service reminder alert

    # Signal and Connection
    "rf_signal_strength_dbm",          # WiFi signal strength
    "rf_signal_bars",                  # WiFi signal quality

    # System Stats
    "days_in_operation",               # Total days system has been running
    "power_outage_count",              # Number of power outages
    "service_reminder_months",         # Months until service needed
    "time_lost_events",                # Time lost events count

    # Additional sensors enabled for debugging/inspection
    "iron_level_tenths_ppm",           # Iron level in water
    "tlc_avg_temp_tenths_c",           # TLC average temperature
    "salt_effic_grains_per_lb",        # Salt efficiency
    "salt_type_enum",                  # Salt type
    "water_counter_gals",              # Water counter
    "error_code",                      # Error code number
    "service_active",                  # Service mode active
    "product_serial_number",           # Device serial number
    "location",                        # Device location
    "system_type",                     # System type
    "model_display_code",              # Model display code
    "base_software_version",           # Base software version
    "esp_software_part_number",        # ESP software part number
    "regen_time_secs",                 # Regeneration time setting
    "system_error",                    # System error status
    "vacation_mode",                   # Vacation mode status
}

# Descriptions for each sensor
SENSOR_DESCRIPTIONS = {
    # BASIC SYSTEM INFORMATION
    "_internal_is_online": {
        "name": "Online Status",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:wifi-check",
        "category": "BASIC",
    },
    # BASIC SYSTEM INFO
    "app_active": {
        "name": "App Active",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:checkbox-marked-circle",
        "category": "BASIC",
    },
    "current_time_secs": {
        "name": "Device Time",
        "unit": None,
        "device_class": SensorDeviceClass.TIMESTAMP,
        "state_class": None,
        "icon": "mdi:clock-outline",
        "category": "BASIC",
    },
    "model_description": {
        "name": "Model",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-well",
        "category": "BASIC",
    },
    "nickname": {
        "name": "Device Name",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:label-outline",
        "category": "BASIC",
    },

    # WATER METRICS
    "current_water_flow_gpm": {
        "name": "Current Water Flow",
        "unit": "gpm",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:water-outline",
        "category": "WATER",
    },
    "gallons_used_today": {
        "name": "Water Used Today",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:water",
        "category": "WATER",
    },
    "avg_daily_use_gals": {
        "name": "Average Daily Water Usage",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:chart-timeline-variant",
        "category": "WATER",
    },
    "total_outlet_water_gals": {
        "name": "Total Treated Water",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:meter-water",
        "category": "WATER",
    },
    "peak_water_flow_gpm": {
        "name": "Peak Water Flow",
        "unit": "gpm",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:chart-bell-curve",
        "category": "WATER",
    },
    "treated_water_avail_gals": {
        "name": "Available Treated Water",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:water-check",
        "category": "WATER",
    },

    # SALT METRICS
    # Note: salt_level_tenths is automatically divided by 10 (API sends 750 for 75%)
    "salt_level_tenths": {
        "name": "Salt Level",
        "unit": PERCENTAGE,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:salt",
        "category": "SALT",
    },
    "out_of_salt_estimate_days": {
        "name": "Days Until Salt Needed",
        "unit": UnitOfTime.DAYS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:calendar-clock",
        "category": "SALT",
    },
    "avg_salt_per_regen_lbs": {
        "name": "Salt Used per Regeneration",
        "unit": UnitOfMass.POUNDS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:scale-bathroom",
        "category": "SALT",
    },
    "total_salt_use_lbs": {
        "name": "Total Salt Used",
        "unit": UnitOfMass.POUNDS,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:scale",
        "category": "SALT",
    },

    # PERFORMANCE METRICS
    "capacity_remaining_percent": {
        "name": "Capacity Remaining",
        "unit": PERCENTAGE,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:water-percent",
        "category": "PERFORMANCE",
    },
    "operating_capacity_grains": {
        "name": "Operating Capacity",
        "unit": "grains",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:water",
        "category": "PERFORMANCE",
    },
    "hardness_grains": {
        "name": "Water Hardness",
        "unit": "grains",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:water-outline",
        "category": "PERFORMANCE",
    },
    "rock_removed_since_rech_lbs": {
        "name": "Hardness Removed Since Recharge",
        "unit": UnitOfMass.POUNDS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:scale",
        "category": "PERFORMANCE",
    },
    "daily_avg_rock_removed_lbs": {
        "name": "Average Daily Hardness Removed",
        "unit": UnitOfMass.POUNDS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:scale-bathroom",
        "category": "PERFORMANCE",
    },
    "total_rock_removed_lbs": {
        "name": "Total Hardness Removed",
        "unit": UnitOfMass.POUNDS,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:scale",
        "category": "PERFORMANCE",
    },

    # REGENERATION STATUS
    "regen_status_enum": {
        "name": "Regeneration Status",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:sync",
        "category": "REGEN",
    },
    "days_since_last_regen": {
        "name": "Days Since Last Regeneration",
        "unit": UnitOfTime.DAYS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:calendar-clock",
        "category": "REGEN",
    },
    "total_regens": {
        "name": "Total Regenerations",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:refresh",
        "category": "REGEN",
    },
    "manual_regens": {
        "name": "Manual Regenerations",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:refresh",
        "category": "REGEN",
    },
    "regen_time_rem_secs": {
        "name": "Regeneration Time Remaining",
        "unit": UnitOfTime.SECONDS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:timer",
        "category": "REGEN",
    },

    # ALERTS
    "low_salt_alert": {
        "name": "Low Salt Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:alert-circle",
        "category": "ALERTS",
    },
    "error_code_alert": {
        "name": "Error Code Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:alert",
        "category": "ALERTS",
    },
    "flow_monitor_alert": {
        "name": "Flow Monitor Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-alert",
        "category": "ALERTS",
    },
    "excessive_water_use_alert": {
        "name": "Excessive Water Use Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-alert",
        "category": "ALERTS",
    },
    "floor_leak_detector_alert": {
        "name": "Leak Detector Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-alert",
        "category": "ALERTS",
    },
    "service_reminder_alert": {
        "name": "Service Reminder Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:tools",
        "category": "ALERTS",
    },

    # SYSTEM STATUS
    "rf_signal_strength_dbm": {
        "name": "WiFi Signal Strength",
        "unit": SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:wifi",
        "category": "SYSTEM",
    },
    "rf_signal_bars": {
        "name": "WiFi Signal Quality",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:wifi",
        "category": "SYSTEM",
    },
    "days_in_operation": {
        "name": "Days in Operation",
        "unit": UnitOfTime.DAYS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:calendar",
        "category": "SYSTEM",
    },
    "power_outage_count": {
        "name": "Power Outage Count",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:power-plug-off",
        "category": "SYSTEM",
    },
    "service_reminder_months": {
        "name": "Months Until Service",
        "unit": UnitOfTime.MONTHS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:tools",
        "category": "SYSTEM",
    },

    # ADDITIONAL SENSORS (not enabled by default)
    "iron_level_tenths_ppm": {
        "name": "Iron Level",
        "unit": "ppm",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:test-tube",
        "category": "PERFORMANCE",
    },
    "tlc_avg_temp_tenths_c": {
        "name": "TLC Average Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:thermometer",
        "category": "SYSTEM",
    },
    "salt_effic_grains_per_lb": {
        "name": "Salt Efficiency",
        "unit": "grains/lb",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:percent",
        "category": "SALT",
    },
    "salt_type_enum": {
        "name": "Salt Type",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:salt",
        "category": "SALT",
    },
    "water_counter_gals": {
        "name": "Water Counter",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:counter",
        "category": "WATER",
    },
    "error_code": {
        "name": "Error Code",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:alert-octagon",
        "category": "ALERTS",
    },
    "service_active": {
        "name": "Service Mode Active",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:wrench",
        "category": "MAINTENANCE",
    },
    "time_lost_events": {
        "name": "Time Lost Events",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:clock-alert",
        "category": "SYSTEM",
    },
    "product_serial_number": {
        "name": "Serial Number",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:barcode",
        "category": "BASIC",
    },
    "location": {
        "name": "Location",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:map-marker",
        "category": "BASIC",
    },
    "system_type": {
        "name": "System Type",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-pump",
        "category": "BASIC",
    },
    "model_display_code": {
        "name": "Model Display Code",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:identifier",
        "category": "BASIC",
    },
    "base_software_version": {
        "name": "Base Software Version",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:application",
        "category": "SYSTEM",
    },
    "esp_software_part_number": {
        "name": "ESP Software Part Number",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:chip",
        "category": "SYSTEM",
    },
    "regen_time_secs": {
        "name": "Regeneration Time",
        "unit": UnitOfTime.SECONDS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:timer-sand",
        "category": "REGEN",
    },
    "system_error": {
        "name": "System Error",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:alert",
        "category": "ALERTS",
    },
    "vacation_mode": {
        "name": "Vacation Mode",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:airplane",
        "category": "BASIC",
    },
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the HydroLink sensors from a config entry."""
    import logging
    _LOGGER = logging.getLogger(__name__)
    
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    
    for device in coordinator.data:
        # Assuming 'demand_softener' is the target device type
        if device.get("system_type") != "demand_softener":
            continue

        device_name = device.get("nickname", "EcoWater Softener")
        
        # Log all available properties from API for debugging
        available_props = list(device.get("properties", {}).keys())
        _LOGGER.info(
            "HydroLink device '%s' has %d properties available from API: %s",
            device_name,
            len(available_props),
            ", ".join(sorted(available_props))
        )

        for prop_name, prop_info in device.get("properties", {}).items():
            if isinstance(prop_info, dict) and "value" in prop_info:
                entities.append(HydroLinkSensor(coordinator, device["id"], prop_name, device_name, prop_info))

    _LOGGER.info("Created %d HydroLink sensor entities", len(entities))
    async_add_entities(entities)


class HydroLinkSensor(CoordinatorEntity, SensorEntity):
    """Representation of a HydroLink sensor."""

    def __init__(self, coordinator, device_id, property_name, device_name, prop_info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._property_name = property_name
        self._device_name = device_name

        # Check if the API provides metric-converted values for this property
        self._use_converted = "converted_value" in prop_info

        description = SENSOR_DESCRIPTIONS.get(property_name)
        if description:
            self._attr_name = f"{device_name} {description['name']}"
            self._attr_native_unit_of_measurement = description.get("unit")
            self._attr_device_class = description.get("device_class")
            self._attr_state_class = description.get("state_class")
            self._attr_icon = description.get("icon")
            self._attr_entity_category = description.get("entity_category")
        else:
            self._attr_name = f"{device_name} {property_name.replace('_', ' ').title()}"

        # Override unit with API-provided converted unit (metric for EU region)
        if self._use_converted:
            converted_units = prop_info.get("converted_units", "")
            ha_unit = API_UNIT_MAP.get(converted_units)
            if ha_unit is not None:
                self._attr_native_unit_of_measurement = ha_unit
                # Update device_class for volume sensors switching to liters
                if ha_unit == UnitOfVolume.LITERS and description:
                    self._attr_device_class = description.get("device_class")

        self._attr_unique_id = f"hydrolink_{device_id}_{property_name}"

        # Set whether the entity should be enabled by default
        self._attr_entity_registry_enabled_default = (
            self._property_name in DEFAULT_ENABLED_SENSORS
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        for device in self.coordinator.data:
            if device["id"] == self._device_id:
                prop = device["properties"][self._property_name]

                # Use converted_value (metric) when available, otherwise raw value
                if self._use_converted and "converted_value" in prop:
                    value = prop.get("converted_value")
                else:
                    value = prop.get("value")

                # Handle numeric sensors when value is unknown
                if (value == "unknown" and self.device_class in [
                    SensorDeviceClass.ENERGY,
                    SensorDeviceClass.POWER,
                    SensorDeviceClass.CURRENT,
                    SensorDeviceClass.VOLTAGE,
                    SensorDeviceClass.PRESSURE,
                    SensorDeviceClass.TEMPERATURE
                ]):
                    return None

                # Convert values that are provided in tenths
                # API sends values like salt_level_tenths as 750 meaning 75.0%
                # Also applies to iron_level_tenths_ppm, capacity_remaining_percent, etc.
                if isinstance(value, (int, float)):
                    # Handle properties with "_tenths" in the name (even if not at the end)
                    if "_tenths" in self._property_name:
                        return value / 10

                    # capacity_remaining_percent is also in tenths
                    if self._property_name == "capacity_remaining_percent":
                        return value / 10

                    # Salt values are provided in thousandths, need to divide by 1000
                    if self._property_name in ["avg_salt_per_regen_lbs", "total_salt_use_lbs"]:
                        return value / 1000

                return value
        return None

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "EcoWater",
        }
