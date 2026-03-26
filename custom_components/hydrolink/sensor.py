# -*- coding: utf-8 -*-
"""EcoWater HydroLink sensor platform."""

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
    "_internal_is_online",
    "app_active",
    "current_time_secs",
    "model_description",
    "nickname",
    "current_water_flow_gpm",
    "gallons_used_today",
    "avg_daily_use_gals",
    "total_outlet_water_gals",
    "peak_water_flow_gpm",
    "treated_water_avail_gals",
    "salt_level_tenths",
    "out_of_salt_estimate_days",
    "avg_salt_per_regen_lbs",
    "total_salt_use_lbs",
    "capacity_remaining_percent",
    "operating_capacity_grains",
    "hardness_grains",
    "rock_removed_since_rech_lbs",
    "daily_avg_rock_removed_lbs",
    "total_rock_removed_lbs",
    "regen_status_enum",
    "days_since_last_regen",
    "total_regens",
    "manual_regens",
    "regen_time_rem_secs",
    "low_salt_alert",
    "error_code_alert",
    "flow_monitor_alert",
    "excessive_water_use_alert",
    "floor_leak_detector_alert",
    "service_reminder_alert",
    "rf_signal_strength_dbm",
    "rf_signal_bars",
    "days_in_operation",
    "power_outage_count",
    "service_reminder_months",
    "time_lost_events",
    "iron_level_tenths_ppm",
    "tlc_avg_temp_tenths_c",
    "salt_effic_grains_per_lb",
    "salt_type_enum",
    "water_counter_gals",
    "error_code",
    "service_active",
    "product_serial_number",
    "location",
    "system_type",
    "model_display_code",
    "base_software_version",
    "esp_software_part_number",
    "regen_time_secs",
    "system_error",
    "vacation_mode",
}

SENSOR_DESCRIPTIONS = {
    "_internal_is_online": {
        "name": "Online Status",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:wifi-check",
        "category": "BASIC",
    },
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
                    if self._property_name in ("avg_salt_per_regen_lbs", "total_salt_use_lbs"):
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
