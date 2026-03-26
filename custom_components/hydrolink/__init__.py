# -*- coding: utf-8 -*-
"""
EcoWater HydroLink Home Assistant Integration

Main module for the Home Assistant integration with EcoWater HydroLink water softeners.
Provides real-time monitoring, control, and alerting capabilities through the HydroLink
cloud service. Handles component setup, config flow, service registration, and data
coordination.

This integration offers comprehensive monitoring of water usage, salt levels, system
performance, regeneration status, and maintenance alerts with real-time WebSocket updates.

Author: GrumpyTanker + AI Assistant
Created: June 12, 2025
Updated: October 3, 2025

Version History:
- 1.3.0 (2026-03-26) - puchalskipl
  * Added multi-region support (United States, Europe)
  * Europe region uses api.hydrolinkhome.eu API endpoint
  * Automatic metric unit conversion for EU (Liters, kg, L/min)
  * Added Polish (pl) translation

- 1.2.0 (2025-10-03)
  * Enhanced documentation and inline comments
  * Improved version compatibility across HA releases
  * Multi-version testing with tox (Python 3.9-3.11)
  * Comprehensive code quality improvements
  * Fixed ConfigEntry API compatibility issues
  * CI/CD pipeline stabilization

- 1.0.0 (2025-10-03)
  * HACS compatibility and validation
  * Enhanced documentation and comments
  * Improved error handling and logging
  * Added comprehensive test coverage
  * WebSocket real-time updates
  * Service calls for manual regeneration
  * 30+ sensors across 8 categories
  
- 0.2.0 (2025-10-02)
  * Added service registration
  * Improved error handling
  * Added type hints and data coordinator
  * Enhanced data organization
  
- 0.1.0 (2025-06-12)
  * Initial release based on Hydrolink-Home-Status
  * Basic integration setup and config flow

License: MIT
See LICENSE file in the project root for full license information.
"""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

# Since we use config flow, this is an empty schema
CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)
from .coordinator import HydroLinkDataUpdateCoordinator
from .services import async_setup_services

PLATFORMS = [Platform.SENSOR]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HydroLink component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HydroLink from a config entry.

    This function is called when a config entry is created for the integration.
    It initializes the data coordinator and forwards the setup to the sensor
    platform.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.

    Returns:
        True if the setup was successful.
    """
    # Ensure the domain data is initialized
    hass.data.setdefault(DOMAIN, {})

    # Create and initialize the data update coordinator
    coordinator = HydroLinkDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator in the hass data
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Set up services
    await async_setup_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    This function is called when a config entry is removed. It unloads the
    sensor platform and removes the coordinator from the hass data.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.

    Returns:
        True if the unload was successful.
    """
    # Unload the platforms associated with the config entry
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Remove the coordinator from the hass data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
