# -*- coding: utf-8 -*-
"""EcoWater HydroLink configuration flow."""
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_REGION, REGIONS, REGION_EU
from .api import HydroLinkApi, CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)

REGION_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_REGION, default=REGION_EU): vol.In(
            {key: config["name"] for key, config in REGIONS.items()}
        ),
    }
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HydroLink."""

    VERSION = 1
    DOMAIN = DOMAIN
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize the config flow."""
        self._region: str = REGION_EU

    async def async_step_user(self, user_input=None):
        """Handle the region selection step."""
        if user_input is not None:
            self._region = user_input[CONF_REGION]
            return await self.async_step_credentials()

        return self.async_show_form(
            step_id="user",
            data_schema=REGION_SCHEMA,
        )

    async def async_step_credentials(self, user_input=None):
        """Handle the credentials step."""
        errors = {}
        if user_input is not None:
            if not user_input.get(CONF_EMAIL) or not user_input.get(CONF_PASSWORD):
                errors["base"] = "invalid_auth"
                return self.async_show_form(
                    step_id="credentials",
                    data_schema=DATA_SCHEMA,
                    errors=errors,
                )

            try:
                api = HydroLinkApi(
                    user_input[CONF_EMAIL],
                    user_input[CONF_PASSWORD],
                    self._region,
                )

                try:
                    await self.hass.async_add_executor_job(api.login)
                except (InvalidAuth, CannotConnect) as err:
                    raise err
                except Exception as err:
                    _LOGGER.exception("Unexpected API error")
                    raise CannotConnect from err

                await self.async_set_unique_id(user_input[CONF_EMAIL])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_EMAIL],
                    data={**user_input, CONF_REGION: self._region},
                )

            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Failed to create API instance")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="credentials",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
