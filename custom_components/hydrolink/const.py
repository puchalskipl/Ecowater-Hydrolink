# -*- coding: utf-8 -*-
"""EcoWater HydroLink constants."""

DOMAIN = "hydrolink"
DEFAULT_UPDATE_INTERVAL = 300  # 5 minutes

CONF_REGION = "region"

REGION_US = "united_states"
REGION_EU = "europe"

REGIONS = {
    REGION_US: {
        "name": "United States",
        "base_url": "https://api.hydrolinkhome.com/v1",
        "ws_base_url": "wss://api.hydrolinkhome.com",
        "auth_cookie_name": "hhfoffoezyzzoeibwv",
    },
    REGION_EU: {
        "name": "Europe",
        "base_url": "https://api.hydrolinkhome.eu/v1",
        "ws_base_url": "wss://api.hydrolinkhome.eu",
        "auth_cookie_name": "hhxaifhduswhaiunzp",
    },
}

PLATFORMS = ["sensor"]

SERVICE_TRIGGER_REGENERATION = "trigger_regeneration"
