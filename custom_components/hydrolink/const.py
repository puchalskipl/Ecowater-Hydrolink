# -*- coding: utf-8 -*-
"""EcoWater HydroLink constants."""

DOMAIN = "hydrolink"

CONF_REGION = "region"

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
