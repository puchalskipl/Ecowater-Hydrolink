# -*- coding: utf-8 -*-
"""
EcoWater HydroLink Data Update Coordinator

Manages data synchronization and updates between the HydroLink cloud API and 
Home Assistant entities. Provides centralized data management with real-time
WebSocket updates, intelligent polling, and comprehensive error handling.

Key Features:
- Centralized data update coordination for all HydroLink entities
- Real-time WebSocket integration for immediate updates
- Intelligent polling with configurable update intervals
- Robust error handling and connection management
- Automatic retry logic for failed API calls
- Data validation and state management
- Integration with Home Assistant's coordinator pattern

This coordinator serves as the bridge between the HydroLink API and all 
sensor entities, ensuring consistent data flow and optimal performance
while minimizing API calls and respecting rate limits.

Author: GrumpyTanker + AI Assistant
Created: June 12, 2025
Updated: October 3, 2025

Version History:
- 1.3.0 (2026-03-26) - puchalskipl
  * Pass region from config entry to HydroLinkApi
  * Backward compatible: defaults to US region for existing entries

- 1.2.0 (2025-10-03)
  * Enhanced documentation and code organization
  * Improved version compatibility testing
  * Code quality and standards improvements
  * Better error handling patterns
  * Comprehensive testing coverage

- 1.0.0 (2025-10-03)
  * Production release with enhanced stability
  * Improved error handling and recovery
  * Optimized update intervals and API efficiency
  * Enhanced logging and diagnostic capabilities
  * Better integration with Home Assistant lifecycle
  
- 0.2.0 (2025-10-02)
  * Added WebSocket support for real-time updates
  * Improved error handling and retry logic
  * Added comprehensive type hints
  * Enhanced data validation and processing
  
- 0.1.0 (2025-06-12)
  * Initial release with basic coordination
  * Polling implementation and data management
  * Foundation for entity data updates

License: MIT
See LICENSE file in the project root for full license information.
"""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from .api import HydroLinkApi, CannotConnect, InvalidAuth
from .const import DOMAIN, CONF_REGION, REGION_US

_LOGGER = logging.getLogger(__name__)


class HydroLinkDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching HydroLink data from the API."""

    def __init__(self, hass: HomeAssistant, entry):
        """Initialize the data update coordinator.

        Args:
            hass: The Home Assistant instance.
            entry: The config entry for this integration.
        """
        self.api = HydroLinkApi(
            entry.data[CONF_EMAIL],
            entry.data[CONF_PASSWORD],
            entry.data.get(CONF_REGION, REGION_US),
        )
        # Initialize the DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Fetch data from the API endpoint.

        This method is called by the DataUpdateCoordinator to refresh the data.
        It calls the API to get the latest device data and handles potential
        connection or authentication errors.

        Returns:
            The latest data from the API.

        Raises:
            UpdateFailed: If the API call fails due to authentication or
                connection issues.
        """
        try:
            # Fetch the data from the API
            return await self.hass.async_add_executor_job(self.api.get_data)
        except InvalidAuth as err:
            raise UpdateFailed("Invalid authentication") from err
        except CannotConnect as err:
            raise UpdateFailed("Error communicating with API") from err
