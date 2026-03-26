# -*- coding: utf-8 -*-
"""EcoWater HydroLink sensor platform."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfVolume,
    UnitOfTime,
    UnitOfMass,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

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

DEFAULT_ENABLED_SENSORS = {
    # Daily monitoring
    "_internal_is_online",
    "salt_level_tenths",
    "out_of_salt_estimate_days",
    "gallons_used_today",
    "current_water_flow_gpm",
    "regen_status_enum",
    # Weekly overview
    "avg_daily_use_gals",
    "capacity_remaining_percent",
    "days_since_last_regen",
    "rf_signal_strength_dbm",
    # Alerts (for automations)
    "low_salt_alert",
    "error_code_alert",
    "excessive_water_use_alert",
    "floor_leak_detector_alert",
    # Long-term statistics (Energy Dashboard)
    "total_outlet_water_gals",
    "total_salt_use_lbs",
    "total_regens",
}

SENSOR_DESCRIPTIONS = {
    # --- BASIC ---
    "_internal_is_online": {
        "name": "Online Status",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:wifi-check",
    },
    "model_description": {
        "name": "Model",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-well",
    },
    "product_serial_number": {
        "name": "Serial Number",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:barcode",
    },

    # --- WATER ---
    "current_water_flow_gpm": {
        "name": "Current Water Flow",
        "unit": "gpm",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:water-outline",
    },
    "gallons_used_today": {
        "name": "Water Used Today",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:water",
    },
    "avg_daily_use_gals": {
        "name": "Average Daily Water Usage",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:chart-timeline-variant",
    },
    "total_outlet_water_gals": {
        "name": "Total Treated Water",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:meter-water",
    },
    "total_untreated_water_gals": {
        "name": "Total Untreated Water",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:water-off",
    },
    "peak_water_flow_gpm": {
        "name": "Peak Water Flow",
        "unit": "gpm",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:chart-bell-curve",
    },
    "treated_water_avail_gals": {
        "name": "Available Treated Water",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:water-check",
    },
    "water_counter_gals": {
        "name": "Water Counter",
        "unit": UnitOfVolume.GALLONS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:counter",
    },

    # --- SALT ---
    "salt_level_tenths": {
        "name": "Salt Level",
        "unit": PERCENTAGE,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:salt",
    },
    "out_of_salt_estimate_days": {
        "name": "Days Until Salt Needed",
        "unit": UnitOfTime.DAYS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:calendar-clock",
    },
    "avg_salt_per_regen_lbs": {
        "name": "Salt Used per Regeneration",
        "unit": UnitOfMass.POUNDS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:scale-bathroom",
    },
    "total_salt_use_lbs": {
        "name": "Total Salt Used",
        "unit": UnitOfMass.POUNDS,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:scale",
    },

    # --- PERFORMANCE ---
    "capacity_remaining_percent": {
        "name": "Capacity Remaining",
        "unit": PERCENTAGE,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:water-percent",
    },
    "average_exhaustion_percent": {
        "name": "Average Exhaustion",
        "unit": PERCENTAGE,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:water-percent",
    },

    # --- REGENERATION ---
    "regen_status_enum": {
        "name": "Regeneration Status",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:sync",
    },
    "days_since_last_regen": {
        "name": "Days Since Last Regeneration",
        "unit": UnitOfTime.DAYS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:calendar-clock",
    },
    "avg_days_between_regens": {
        "name": "Average Days Between Regenerations",
        "unit": UnitOfTime.DAYS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:calendar-range",
    },
    "total_regens": {
        "name": "Total Regenerations",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:refresh",
    },
    "manual_regens": {
        "name": "Manual Regenerations",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:refresh",
    },
    "regen_time_rem_secs": {
        "name": "Regeneration Time Remaining",
        "unit": UnitOfTime.SECONDS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:timer",
    },
    "current_valve_position_enum": {
        "name": "Valve Position",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:valve",
    },

    # --- ALERTS ---
    "low_salt_alert": {
        "name": "Low Salt Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:alert-circle",
    },
    "error_code": {
        "name": "Error Code",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:alert-octagon",
    },
    "error_code_alert": {
        "name": "Error Code Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:alert",
    },
    "depletion_alert": {
        "name": "Depletion Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-alert",
    },
    "flow_monitor_alert": {
        "name": "Flow Monitor Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-alert",
    },
    "excessive_water_use_alert": {
        "name": "Excessive Water Use Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-alert",
    },
    "floor_leak_detector_alert": {
        "name": "Leak Detector Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-alert",
    },
    "wtd_alert": {
        "name": "Water to Drain Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:water-alert",
    },
    "service_reminder_alert": {
        "name": "Service Reminder Alert",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:tools",
    },

    # --- SYSTEM ---
    "rf_signal_strength_dbm": {
        "name": "WiFi Signal Strength",
        "unit": SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:wifi",
    },
    "rf_signal_bars": {
        "name": "WiFi Signal Quality",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:wifi",
    },
    "wifi_ssid": {
        "name": "WiFi SSID",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:wifi-settings",
    },
    "days_in_operation": {
        "name": "Days in Operation",
        "unit": UnitOfTime.DAYS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:calendar",
    },
    "power_outage_count": {
        "name": "Power Outage Count",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:power-plug-off",
    },
    "time_lost_events": {
        "name": "Time Lost Events",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:clock-alert",
    },
    "service_reminder_months": {
        "name": "Months Until Service",
        "unit": UnitOfTime.MONTHS,
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:tools",
    },
    "service_active": {
        "name": "Service Mode Active",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:wrench",
    },
    "base_software_version": {
        "name": "Base Software Version",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:application",
    },
    "esp_software_part_number": {
        "name": "ESP Software Part Number",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:chip",
    },
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the HydroLink sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device in coordinator.data:
        if device.get("system_type") != "demand_softener":
            continue

        device_name = device.get("nickname", "EcoWater Softener")

        _LOGGER.debug(
            "HydroLink device '%s': %d properties",
            device_name,
            len(device.get("properties", {})),
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
        self._use_converted = "converted_value" in prop_info

        self._attr_has_entity_name = True

        description = SENSOR_DESCRIPTIONS.get(property_name)
        if description:
            self._attr_translation_key = property_name
            self._attr_native_unit_of_measurement = description.get("unit")
            self._attr_device_class = description.get("device_class")
            self._attr_state_class = description.get("state_class")
            self._attr_icon = description.get("icon")
            self._attr_entity_category = description.get("entity_category")
        else:
            self._attr_name = property_name.replace("_", " ").title()

        if self._use_converted:
            converted_units = prop_info.get("converted_units", "")
            ha_unit = API_UNIT_MAP.get(converted_units)
            if ha_unit is not None:
                self._attr_native_unit_of_measurement = ha_unit
                if ha_unit == UnitOfVolume.LITERS and description:
                    self._attr_device_class = description.get("device_class")

        self._attr_unique_id = f"hydrolink_{device_id}_{property_name}"
        self._attr_entity_registry_enabled_default = (
            self._property_name in DEFAULT_ENABLED_SENSORS
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        for device in self.coordinator.data:
            if device["id"] == self._device_id:
                # Salt level: use enriched_data percentage instead of raw sensor reading
                if self._property_name == "salt_level_tenths":
                    enriched = device.get("enriched_data", {})
                    wt = enriched.get("water_treatment", {})
                    sl = wt.get("salt_level", {})
                    percent = sl.get("salt_level_percent")
                    if percent is not None:
                        return percent
                    return device["properties"][self._property_name].get("value", 0) / 10

                prop = device["properties"][self._property_name]

                if self._use_converted and "converted_value" in prop:
                    value = prop.get("converted_value")
                else:
                    value = prop.get("value")

                if (value == "unknown" and self.device_class in [
                    SensorDeviceClass.ENERGY, SensorDeviceClass.POWER,
                    SensorDeviceClass.CURRENT, SensorDeviceClass.VOLTAGE,
                    SensorDeviceClass.PRESSURE, SensorDeviceClass.TEMPERATURE,
                ]):
                    return None

                # Scale values stored in tenths or thousandths by the API
                if isinstance(value, (int, float)):
                    if "_tenths" in self._property_name:
                        return value / 10
                    if self._property_name == "capacity_remaining_percent":
                        return value / 10
                    if self._property_name == "average_exhaustion_percent":
                        return value / 10
                    if self._property_name == "avg_days_between_regens":
                        return value / 100
                    if self._property_name == "total_salt_use_lbs":
                        return value / 10
                    if self._property_name == "avg_salt_per_regen_lbs":
                        return value / 10000

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
