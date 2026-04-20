# -*- coding: utf-8 -*-
"""EcoWater HydroLink constants."""

DOMAIN = "hydrolink"

CONF_REGION = "region"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL_MINUTES = 5
MIN_SCAN_INTERVAL_MINUTES = 1
MAX_SCAN_INTERVAL_MINUTES = 60

REGION_COM = "hydrolinkhome_com"
REGION_EU = "hydrolinkhome_eu"

REGIONS = {
    REGION_COM: {
        "name": "hydrolinkhome.com",
        "base_url": "https://api.hydrolinkhome.com/v1",
        "ws_base_url": "wss://api.hydrolinkhome.com",
        "auth_cookie_name": "hhfoffoezyzzoeibwv",
    },
    REGION_EU: {
        "name": "hydrolinkhome.eu",
        "base_url": "https://api.hydrolinkhome.eu/v1",
        "ws_base_url": "wss://api.hydrolinkhome.eu",
        "auth_cookie_name": "hhxaifhduswhaiunzp",
    },
}

PLATFORMS = ["sensor"]

SERVICE_TRIGGER_REGENERATION = "trigger_regeneration"
