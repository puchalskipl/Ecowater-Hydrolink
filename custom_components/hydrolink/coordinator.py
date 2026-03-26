# -*- coding: utf-8 -*-
"""EcoWater HydroLink data update coordinator."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from .api import HydroLinkApi, CannotConnect, InvalidAuth
from .const import DOMAIN, CONF_REGION, REGION_US

_LOGGER = logging.getLogger(__name__)


class HydroLinkDataUpdateCoordinator(DataUpdateCoordinator):
    """Manage fetching HydroLink data from the API."""

    def __init__(self, hass: HomeAssistant, entry):
        """Initialize the coordinator."""
        self.api = HydroLinkApi(
            entry.data[CONF_EMAIL],
            entry.data[CONF_PASSWORD],
            entry.data.get(CONF_REGION, REGION_US),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Fetch data from the API."""
        try:
            return await self.hass.async_add_executor_job(self.api.get_data)
        except InvalidAuth as err:
            raise UpdateFailed("Invalid authentication") from err
        except CannotConnect as err:
            raise UpdateFailed("Error communicating with API") from err
