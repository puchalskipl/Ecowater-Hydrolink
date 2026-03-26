# EcoWater HydroLink - Complete Sensor Documentation

This document provides comprehensive documentation for all available sensors and variables provided by the EcoWater HydroLink Home Assistant integration.

## Table of Contents

- [Overview](#overview)
- [Sensor Categories](#sensor-categories)
- [Complete Sensor List](#complete-sensor-list)
  - [Basic System Information](#basic-system-information)
  - [Water Usage Metrics](#water-usage-metrics)
  - [Salt Management](#salt-management)
  - [System Performance](#system-performance)
  - [Regeneration Status](#regeneration-status)
  - [Alerts and Warnings](#alerts-and-warnings)
  - [System Status](#system-status)
- [Data Types and Units](#data-types-and-units)
- [State Classes](#state-classes)
- [API Variable Mapping](#api-variable-mapping)

---

## Overview

The EcoWater HydroLink integration provides **30+ sensors** organized into **7 major categories**. Each sensor is automatically created when the integration is set up and updates in real-time via WebSocket connections to the HydroLink cloud service.

### Update Frequency
- **Real-time Updates**: WebSocket-based for immediate changes
- **Polling Interval**: 30 seconds (configurable)
- **Connection**: Cloud-based via HydroLink service

---

## Sensor Categories

| Category | Sensors | Description |
|----------|---------|-------------|
| **Basic System Information** | 5 | Device identity, connectivity, and basic status |
| **Water Usage Metrics** | 6 | Flow rates, consumption, and usage tracking |
| **Salt Management** | 4 | Salt levels, efficiency, and usage |
| **System Performance** | 6 | Capacity, hardness, and treatment metrics |
| **Regeneration Status** | 5 | Regeneration cycles, timing, and history |
| **Alerts and Warnings** | 6 | System alerts and maintenance notifications |
| **System Status** | 5 | Connectivity, signal strength, and uptime |

**Total: 37 sensors**

---

## Complete Sensor List

### Basic System Information

Information about the device identity and connectivity status.

| Sensor Name | Entity ID | Unit | Device Class | State Class | Description |
|-------------|-----------|------|--------------|-------------|-------------|
| **Online Status** | `sensor.hydrolink_online_status` | - | - | - | Current connectivity status to HydroLink cloud |
| **System Error** | `sensor.hydrolink_system_error` | - | - | - | Active system error code or state |
| **Vacation Mode** | `sensor.hydrolink_vacation_mode` | - | - | - | Indicates if vacation mode is enabled |
| **Model** | `sensor.hydrolink_model` | - | - | - | Water softener model name/number |
| **Device Name** | `sensor.hydrolink_device_name` | - | - | - | User-configured device nickname |
| **Device Time** | `sensor.hydrolink_device_time` | - | Timestamp | - | Current device time from system clock |

**Icon**: `mdi:wifi`, `mdi:alert`, `mdi:airplane`, `mdi:water-well`, `mdi:label-outline`

---

### Water Usage Metrics

Comprehensive water flow and usage monitoring.

| Sensor Name | Entity ID | Unit | Device Class | State Class | Description |
|-------------|-----------|------|--------------|-------------|-------------|
| **Current Water Flow** | `sensor.hydrolink_current_water_flow` | GPM | - | Measurement | Real-time water flow rate through the system |
| **Water Used Today** | `sensor.hydrolink_water_used_today` | Gallons | - | Total Increasing | Total water consumption for current day |
| **Average Daily Water Usage** | `sensor.hydrolink_avg_daily_water_usage` | Gallons | - | Measurement | Rolling average of daily water consumption |
| **Total Treated Water** | `sensor.hydrolink_total_treated_water` | Gallons | - | Total Increasing | Lifetime total of treated water |
| **Peak Water Flow** | `sensor.hydrolink_peak_water_flow` | GPM | - | Measurement | Maximum recorded flow rate |
| **Available Treated Water** | `sensor.hydrolink_available_treated_water` | Gallons | - | Measurement | Remaining treated water before regeneration needed |

**Icons**: `mdi:water-outline`, `mdi:water`, `mdi:chart-timeline-variant`, `mdi:meter-water`, `mdi:chart-bell-curve`, `mdi:water-check`

**Example Values**:
- Current Water Flow: `0.0` - `15.0` GPM (typical household)
- Water Used Today: `0` - `500` gallons (varies by household size)
- Average Daily Usage: `80` - `150` gallons per person

---

### Salt Management

Salt level monitoring and efficiency tracking.

> **Technical Note**: The HydroLink API provides salt level in tenths (e.g., 750 = 75%). The integration automatically converts this to percentage by dividing by 10.

| Sensor Name | Entity ID | Unit | Device Class | State Class | Description |
|-------------|-----------|------|--------------|-------------|-------------|
| **Salt Level** | `sensor.hydrolink_salt_level` | % | - | Measurement | Current salt reservoir level (0-100%) |
| **Days Until Salt Needed** | `sensor.hydrolink_days_until_salt_needed` | Days | - | Measurement | Estimated days before salt refill required |
| **Salt Used per Regeneration** | `sensor.hydrolink_salt_per_regen` | lbs | - | Measurement | Average salt consumed per regeneration cycle |
| **Total Salt Used** | `sensor.hydrolink_total_salt_used` | lbs | - | Total Increasing | Lifetime salt consumption |

**Icons**: `mdi:salt`, `mdi:calendar-clock`, `mdi:scale-bathroom`, `mdi:scale`

**Thresholds**:
- **Salt Level**:
  - 🟢 Above 50%: Good
  - 🟡 25-50%: Monitor
  - 🔴 Below 25%: Refill Soon
  - ⚠️ Below 10%: Low Salt Alert triggered

**Example Values**:
- Salt Level: `75%` (typical healthy level)
- Days Until Needed: `45` - `90` days (varies by usage)
- Salt per Regen: `6` - `12` lbs (model-dependent)

---

### System Performance

Water treatment efficiency and capacity metrics.

| Sensor Name | Entity ID | Unit | Device Class | State Class | Description |
|-------------|-----------|------|--------------|-------------|-------------|
| **Capacity Remaining** | `sensor.hydrolink_capacity_remaining` | % | - | Measurement | Remaining treatment capacity before regeneration |
| **Operating Capacity** | `sensor.hydrolink_operating_capacity` | Grains | - | Measurement | Total system treatment capacity in grains |
| **Water Hardness** | `sensor.hydrolink_water_hardness` | Grains | - | Measurement | Current water hardness level (grains per gallon) |
| **Hardness Removed Since Recharge** | `sensor.hydrolink_hardness_removed_recent` | lbs | - | Measurement | Hardness removed since last regeneration |
| **Average Daily Hardness Removed** | `sensor.hydrolink_avg_hardness_removed` | lbs | - | Measurement | Average daily hardness treatment |
| **Total Hardness Removed** | `sensor.hydrolink_total_hardness_removed` | lbs | - | Total Increasing | Lifetime hardness treatment total |

**Icons**: `mdi:water-percent`, `mdi:water`, `mdi:water-outline`, `mdi:scale`

**Water Hardness Classifications**:
- 0-3 grains: Soft
- 3-7 grains: Moderate
- 7-10 grains: Hard
- 10+ grains: Very Hard

**Example Values**:
- Capacity Remaining: `0%` - `100%` (triggers regen near 0%)
- Operating Capacity: `30,000` - `64,000` grains (model-dependent)
- Water Hardness: `5` - `15` grains (location-dependent)

---

### Regeneration Status

Monitoring and tracking of water softener regeneration cycles.

| Sensor Name | Entity ID | Unit | Device Class | State Class | Description |
|-------------|-----------|------|--------------|-------------|-------------|
| **Regeneration Status** | `sensor.hydrolink_regen_status` | - | - | - | Current regeneration cycle state |
| **Days Since Last Regeneration** | `sensor.hydrolink_days_since_regen` | Days | - | Measurement | Time elapsed since last regeneration |
| **Total Regenerations** | `sensor.hydrolink_total_regens` | Count | - | Total Increasing | Lifetime regeneration cycle count |
| **Manual Regenerations** | `sensor.hydrolink_manual_regens` | Count | - | Total Increasing | User-initiated regeneration count |
| **Regeneration Time Remaining** | `sensor.hydrolink_regen_time_remaining` | Seconds | - | Measurement | Time remaining in current regeneration cycle |

**Icons**: `mdi:sync`, `mdi:calendar-clock`, `mdi:refresh`, `mdi:timer`

**Regeneration Status Values**:
- `idle`: Not regenerating
- `backwash`: Cleaning resin bed
- `brine_draw`: Drawing brine through resin
- `rinse`: Rinsing resin bed
- `refill`: Refilling brine tank
- `complete`: Cycle complete

**Typical Cycle Times**:
- Full Regeneration: 90-120 minutes
- Backwash: 10 minutes
- Brine Draw: 60 minutes
- Rinse: 10 minutes
- Refill: 10 minutes

---

### Alerts and Warnings

Proactive system alerts and maintenance notifications.

| Sensor Name | Entity ID | Unit | Device Class | State Class | Description |
|-------------|-----------|------|--------------|-------------|-------------|
| **Low Salt Alert** | `sensor.hydrolink_low_salt_alert` | - | - | - | Salt level below threshold warning |
| **Error Code Alert** | `sensor.hydrolink_error_code_alert` | - | - | - | System error or malfunction indicator |
| **Flow Monitor Alert** | `sensor.hydrolink_flow_monitor_alert` | - | - | - | Abnormal water flow detection |
| **Excessive Water Use Alert** | `sensor.hydrolink_excessive_water_alert` | - | - | - | High water usage warning |
| **Leak Detector Alert** | `sensor.hydrolink_leak_detector_alert` | - | - | - | Water leak detection (if equipped) |
| **Service Reminder Alert** | `sensor.hydrolink_service_reminder_alert` | - | - | - | Scheduled maintenance reminder |

**Icons**: `mdi:alert-circle`, `mdi:alert`, `mdi:water-alert`, `mdi:tools`

**Alert States**:
- `0` or `False`: No alert
- `1` or `True`: Alert active
- May include additional status text depending on alert type

**Common Alert Triggers**:
- **Low Salt**: Triggered at <25% salt level
- **Error Code**: System malfunction detected
- **Flow Monitor**: Continuous flow >2 hours or unusual patterns
- **Excessive Use**: Usage exceeds predicted by >50%
- **Leak Detector**: Floor sensor detects moisture
- **Service Reminder**: Based on time/usage intervals

---

### System Status

Device connectivity, signal strength, and operational metrics.

| Sensor Name | Entity ID | Unit | Device Class | State Class | Description |
|-------------|-----------|------|--------------|-------------|-------------|
| **WiFi Signal Strength** | `sensor.hydrolink_wifi_signal` | dBm | Signal Strength | Measurement | WiFi signal strength in decibels |
| **WiFi Signal Quality** | `sensor.hydrolink_signal_quality` | Bars | - | Measurement | WiFi signal bars (0-4) |
| **Days in Operation** | `sensor.hydrolink_days_in_operation` | Days | - | Measurement | Total days system has been operational |
| **Power Outage Count** | `sensor.hydrolink_power_outages` | Count | - | Total Increasing | Number of detected power failures |
| **Months Until Service** | `sensor.hydrolink_service_due` | Months | - | Measurement | Estimated months until service needed |

**Icons**: `mdi:wifi`, `mdi:calendar`, `mdi:power-plug-off`, `mdi:tools`

**WiFi Signal Strength Guide**:
- -30 to -50 dBm: Excellent (4 bars)
- -50 to -60 dBm: Good (3 bars)
- -60 to -70 dBm: Fair (2 bars)
- -70 to -80 dBm: Weak (1 bar)
- Below -80 dBm: Very Weak (0 bars, connection issues likely)

**Example Values**:
- WiFi Signal: `-45 dBm` (excellent connection)
- Signal Quality: `3` bars
- Days in Operation: `365` days (1 year)
- Power Outages: `2` (since installation)
- Service Due: `11` months (annual service)

---

## Data Types and Units

### Units of Measurement

| Unit Type | Unit | Description |
|-----------|------|-------------|
| **Volume** | Gallons | Water volume measurements |
| **Flow Rate** | GPM (Gallons Per Minute) | Water flow velocity |
| **Mass** | Pounds (lbs) | Salt and hardness weight |
| **Hardness** | Grains | Water hardness (grains per gallon) |
| **Time** | Days, Seconds, Months | Duration measurements |
| **Percentage** | % | Levels and capacity percentages |
| **Signal** | dBm | WiFi signal strength |
| **Count** | - | Numeric counters |

### Imperial vs Metric

⚠️ **Note**: This integration currently uses **Imperial units only** as defined by the EcoWater HydroLink API:
- Volume: Gallons (not liters)
- Mass: Pounds (not kilograms)
- Flow: GPM (not liters per minute)

Home Assistant's unit conversion can be used to display values in preferred units in the UI.

---

## State Classes

The integration uses Home Assistant's state class system for proper data handling:

| State Class | Description | Used For |
|-------------|-------------|----------|
| **Measurement** | Regular measurement values | Flow rates, levels, percentages |
| **Total Increasing** | Cumulative values that only increase | Total water used, total salt used, regen counts |
| **None** | No specific state handling | Status indicators, alerts, text values |

This enables:
- ✅ Proper long-term statistics
- ✅ Energy dashboard compatibility (where applicable)
- ✅ Correct graph rendering
- ✅ Accurate data aggregation

---

## API Variable Mapping

### Value Conversions

The integration automatically performs the following conversions on raw API data:

| Conversion Type | API Format | Displayed Format | Example |
|----------------|------------|------------------|---------|
| **Tenths to Decimal** | Any variable containing `_tenths` | Value / 10 | API: `750` → Display: `75.0%` |
| **Capacity Percent** | `capacity_remaining_percent` | Value / 10 | API: `850` → Display: `85.0%` |
| **Salt Values** | `avg_salt_per_regen_lbs`, `total_salt_use_lbs` | Value / 1000 | API: `6670` → Display: `6.67 lbs` |
| **Timestamp** | `current_time_secs` (Unix epoch) | Formatted datetime | API: `1633046400` → Display: `2021-10-01 00:00:00` |

**Variables Affected by Tenths Conversion (÷10)**:
- `salt_level_tenths`: Tenths to percentage (e.g., 750 → 75.0%)
- `iron_level_tenths_ppm`: Tenths PPM to PPM (e.g., 25 → 2.5 ppm)
- `tlc_avg_temp_tenths_c`: Tenths Celsius to Celsius (e.g., 310 → 31.0°C)
- `capacity_remaining_percent`: Tenths to percentage (e.g., 850 → 85.0%)

**Variables Affected by Salt Conversion (÷1000)**:
- `avg_salt_per_regen_lbs`: Milligrams to pounds (e.g., 6670 → 6.67 lbs)
- `total_salt_use_lbs`: Milligrams to pounds (e.g., 667000 → 667.0 lbs)

This ensures that values display correctly in their expected units.

### Internal API Keys to Sensor Names

The HydroLink API uses specific key names that are mapped to user-friendly sensor names:

| API Key | Sensor Entity | Sensor Name |
|---------|---------------|-------------|
| `_internal_is_online` | `sensor.hydrolink_online_status` | Online Status |
| `current_water_flow_gpm` | `sensor.hydrolink_current_water_flow` | Current Water Flow |
| `gallons_used_today` | `sensor.hydrolink_water_used_today` | Water Used Today |
| `salt_level_tenths` | `sensor.hydrolink_salt_level` | Salt Level |
| `out_of_salt_estimate_days` | `sensor.hydrolink_days_until_salt_needed` | Days Until Salt Needed |
| `capacity_remaining_percent` | `sensor.hydrolink_capacity_remaining` | Capacity Remaining |
| `regen_status_enum` | `sensor.hydrolink_regen_status` | Regeneration Status |
| `days_since_last_regen` | `sensor.hydrolink_days_since_regen` | Days Since Last Regeneration |
| `rf_signal_strength_dbm` | `sensor.hydrolink_wifi_signal` | WiFi Signal Strength |
| `rf_signal_bars` | `sensor.hydrolink_signal_quality` | WiFi Signal Quality |
| `low_salt_alert` | `sensor.hydrolink_low_salt_alert` | Low Salt Alert |
| `error_code_alert` | `sensor.hydrolink_error_code_alert` | Error Code Alert |

**Complete mapping available in**: `custom_components/hydrolink/sensor.py`

---

## Using Sensors in Home Assistant

### Lovelace Card Example

```yaml
type: entities
title: Water Softener Status
entities:
  - entity: sensor.hydrolink_online_status
    name: System Status
  - entity: sensor.hydrolink_salt_level
    name: Salt Level
  - entity: sensor.hydrolink_current_water_flow
    name: Current Flow
  - entity: sensor.hydrolink_water_used_today
    name: Today's Usage
  - entity: sensor.hydrolink_capacity_remaining
    name: Capacity
  - entity: sensor.hydrolink_days_until_salt_needed
    name: Salt Refill
```

### Automation Example

```yaml
automation:
  - alias: "Low Salt Notification"
    trigger:
      - platform: numeric_state
        entity_id: sensor.hydrolink_salt_level
        below: 25
    action:
      - service: notify.mobile_app
        data:
          title: "Water Softener Alert"
          message: "Salt level is low ({{ states('sensor.hydrolink_salt_level') }}%). Please refill soon."
```

### Template Example

```yaml
template:
  - sensor:
      - name: "Water Softener Health"
        state: >
          {% set salt = states('sensor.hydrolink_salt_level') | float(0) %}
          {% set capacity = states('sensor.hydrolink_capacity_remaining') | float(0) %}
          {% if salt > 50 and capacity > 30 %}
            Excellent
          {% elif salt > 25 and capacity > 15 %}
            Good
          {% elif salt > 10 or capacity > 5 %}
            Fair
          {% else %}
            Needs Attention
          {% endif %}
```

---

## Troubleshooting

### Sensor Not Updating

1. **Check Online Status**: Verify `sensor.hydrolink_online_status` shows connected
2. **WiFi Signal**: Check `sensor.hydrolink_wifi_signal` is above -70 dBm
3. **Integration Status**: Settings → Devices & Services → HydroLink
4. **Reload Integration**: Try reloading the integration
5. **Restart HA**: Restart Home Assistant if issues persist

### Missing Sensors

Some sensors may not appear if:
- Device doesn't support that feature (e.g., leak detector on older models)
- API doesn't provide that data point for your specific model
- Sensor is disabled by default (check entity settings)

### Incorrect Values

1. **Check API Data**: Enable debug logging to see raw API responses
2. **Time Zone**: Verify device time zone matches Home Assistant
3. **Unit Conversion**: Ensure no double-conversion of units
4. **Calibration**: Some values may need device recalibration

---

## Additional Resources

- **Main Documentation**: [README.md](README.md)
- **Source Code**: [sensor.py](custom_components/hydrolink/sensor.py)

