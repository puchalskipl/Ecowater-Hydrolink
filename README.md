# EcoWater HydroLink Integration for Home Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![HA Core Version](https://img.shields.io/badge/Home%20Assistant-2024.10.0+-blue.svg)](https://www.home-assistant.io)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org)

A Home Assistant custom component for EcoWater HydroLink connected water softeners. Monitor water usage, salt levels, system performance, and control regeneration — all from Home Assistant.

Based on the original [Hydrolink-Home-Status](https://github.com/GrumpyTanker/Hydrolink-Home-Status) project.

## Features

- Real-time monitoring via WebSocket connections
- 40+ sensors across 8 categories (water usage, salt, performance, regeneration, alerts, signal, maintenance, system)
- Manual regeneration control via service calls
- **Multi-region support**: United States (`api.hydrolinkhome.com`) and Europe (`api.hydrolinkhome.eu`)
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
3. Select your region (United States or Europe)
4. Enter your HydroLink email and password

## Sensors

The integration auto-discovers all sensors from your device (typically 40+). You can enable/disable individual sensors in **Settings → Devices & Services → HydroLink → Entities**.

Default-enabled sensors include:

| Category | Sensors |
|----------|---------|
| **Water Usage** | Current Flow, Water Used Today, Average Daily Usage, Total Treated Water, Peak Flow, Available Treated Water |
| **Salt** | Salt Level (%), Days Until Salt Needed, Salt Per Regeneration, Total Salt Used, Salt Efficiency |
| **Performance** | Capacity Remaining (%), Operating Capacity, Water Hardness, Hardness Removed |
| **Regeneration** | Status, Days Since Last Regen, Total/Manual Regen Count, Time Remaining |
| **Alerts** | Low Salt, Error Code, Flow Monitor, Excessive Water Use, Leak Detector, Service Reminder |
| **System** | Online Status, WiFi Signal (dBm), Signal Bars, Days in Operation, Power Outages |

> **EU Region**: Volume sensors show Liters, mass sensors show kg, flow sensors show L/min.
> **US Region**: Gallons, lbs, GPM (imperial units).

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

### Debug Logging

```yaml
logger:
  logs:
    custom_components.hydrolink: debug
```

## Version History

### 1.3.0 (2026-03-26) — puchalskipl
- Multi-region support (United States / Europe)
- Europe API endpoint (`api.hydrolinkhome.eu`) with separate auth cookie handling
- Automatic metric unit conversion for EU region (Liters, kg, L/min)
- Two-step config flow with region selection
- Polish translation
- Backward compatible with existing config entries (default to US)

### 1.2.2 (2025-10-10)
- Fixed sensor scaling issues (tenths, capacity, salt values)
- Added 15 new sensor definitions
- Added `device_class: water` for Energy Dashboard support

### 1.2.0 (2025-10-03)
- Enhanced documentation, multi-version testing (Python 3.9–3.11)
- ConfigEntry API compatibility fixes, CI/CD stabilization

### 1.0.0 (2025-10-02)
- Initial HACS-compatible release
- 30+ sensors, WebSocket real-time updates, manual regeneration service

## License

MIT — see [LICENSE](LICENSE).

## Trademark Notice

This project is not affiliated with EcoWater Systems LLC. EcoWater and HydroLink are trademarks of EcoWater Systems LLC, used here solely for compatibility identification.
