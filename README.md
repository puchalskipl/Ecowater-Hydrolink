# EcoWater HydroLink Integration for Home Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![HA Core Version](https://img.shields.io/badge/Home%20Assistant-2024.10.0+-blue.svg)](https://www.home-assistant.io)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org)

A Home Assistant custom component for EcoWater HydroLink connected water softeners. Monitor water usage, salt levels, system performance, and control regeneration — all from Home Assistant.

## Features

- Real-time monitoring via WebSocket connections
- ~110 sensors auto-discovered from API, 17 enabled by default
- Manual regeneration control via service calls
- **Multi-region support**: hydrolinkhome.eu (default) and hydrolinkhome.com
- Automatic metric units for EU region (Liters, kg, L/min)
- Polish and English translations

## Installation

### HACS (Recommended)
1. Install [HACS](https://hacs.xyz) if you haven't already
2. Add this repository as a custom repository in HACS
3. Search for "EcoWater HydroLink" and install
4. Restart Home Assistant

### Manual
1. Copy `custom_components/hydrolink` to your HA `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **HydroLink**
3. Select your region (hydrolinkhome.eu is the default, hydrolinkhome.com also available)
4. Enter your HydroLink email and password

### Options

After setup, click **Configure** on the HydroLink card to adjust:

- **Update interval (minutes)** — how often the integration polls the cloud API. Default: 5 minutes (range 1–60). Increase if you keep hitting rate limits; the integration will reload automatically when you save.

## Sensors

The integration auto-discovers all sensors from your device (~110 properties). 17 most useful sensors are enabled by default. You can enable/disable any sensor in **Settings → Devices & Services → HydroLink → Entities**.

Default-enabled sensors (★):

| Category | Sensors |
|----------|---------|
| **Daily** | Online Status, Salt Level (%), Days Until Salt Needed, Water Used Today, Current Flow, Regeneration Status |
| **Weekly** | Average Daily Usage, Capacity Remaining (%), Days Since Last Regen, WiFi Signal |
| **Alerts** | Low Salt, Error Code, Excessive Water Use, Leak Detector |
| **Statistics** | Total Treated Water, Total Salt Used, Total Regenerations |

> **hydrolinkhome.eu**: Volume in Liters, mass in kg, flow in L/min.
> **hydrolinkhome.com**: Gallons, lbs, GPM (imperial units).

Full sensor documentation: [SENSORS.md](SENSORS.md)

## Services

### `hydrolink.trigger_regeneration`
Manually start a regeneration cycle.

| Parameter | Description |
|-----------|-------------|
| `device_id` | The device ID of the water softener |

## Troubleshooting

**Cannot Connect** — Check your internet connection and that the HydroLink service is operational.

**Authentication Failed** — Verify your email and password. Try logging into the HydroLink app to confirm credentials work.

**No Data Updates** — Check your device's connection to HydroLink, then restart Home Assistant.

**Rate Limited (429)** — The HydroLink cloud API enforces request quotas. The integration honors `Retry-After` and uses exponential backoff (cap 15 min); after 3 consecutive 429s it pauses polling for 30 minutes. If you see this often, raise the **Update interval** in Configure.

### Debug Logging

```yaml
logger:
  logs:
    custom_components.hydrolink: debug
```

## Version History

### 1.4.0 (2026-04-20)
- Honors `Retry-After` header on 429 responses with exponential backoff (cap 15 min)
- Circuit breaker pauses polling for 30 minutes after 3 consecutive 429s (logged once as WARNING, not ERROR)
- Configurable poll interval via the Configure dialog (1–60 min, default 5)
- Sensors mark themselves unavailable when the device drops out of the API payload, instead of returning `"unknown"`
- Single shared HTTP request helper used across login, data fetch, and regeneration

### 1.3.0 (2026-03-26)
- Multi-region support (hydrolinkhome.eu default, hydrolinkhome.com)
- Automatic metric unit conversion for EU region (Liters, kg, L/min)
- Two-step config flow with region selection
- Salt level read from enriched_data for accurate percentage
- Corrected salt and regeneration value scaling
- Reduced default-enabled sensors from ~80 to 17 most useful
- Cleaned up sensor definitions (38 explicit, ~70 auto-discovered)
- Polish translation
- Project cleanup and documentation rewrite

### 1.2.2 (2025-10-10)
- Fixed sensor scaling issues (tenths, capacity, salt values)
- Added `device_class: water` for Energy Dashboard support

### 1.2.0 (2025-10-03)
- Multi-version testing (Python 3.9–3.11)
- ConfigEntry API compatibility fixes

### 1.0.0 (2025-10-02)
- Initial HACS-compatible release
- WebSocket real-time updates, manual regeneration service

## License

MIT — see [LICENSE](LICENSE).

## Trademark Notice

This project is not affiliated with EcoWater Systems LLC. EcoWater and HydroLink are trademarks of EcoWater Systems LLC, used here solely for compatibility identification.
