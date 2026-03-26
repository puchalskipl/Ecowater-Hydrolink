# Sensor Documentation

The integration auto-discovers all properties from the HydroLink API and exposes them as sensors. A typical device provides ~100 properties, of which ~55 are enabled by default.

## Units

The API provides values in imperial units. For the **hydrolinkhome.eu** region, the API also returns `converted_value` in metric units, which the integration uses automatically:

| Measurement | hydrolinkhome.com | hydrolinkhome.eu |
|-------------|-------------------|------------------|
| Volume | Gallons | Liters |
| Flow rate | GPM | L/min |
| Mass | lbs | kg |
| Hardness | grains | grains |
| Temperature | °C | °C |
| Signal | dBm | dBm |

## Value Scaling

Some API values are stored in scaled format. The integration converts them automatically:

| Rule | Affected properties | Example |
|------|-------------------|---------|
| Divide by 10 | Any property with `_tenths` in name | `salt_level_tenths`: 750 → 75.0% |
| Divide by 10 | `capacity_remaining_percent` | 300 → 30.0% |
| Divide by 1000 | `avg_salt_per_regen_lbs`, `total_salt_use_lbs` | 17822 → 17.822 lbs / 8.084 kg |

## Default-Enabled Sensors

### Basic System Information

| API Property | Sensor Name | Unit | Icon |
|-------------|-------------|------|------|
| `_internal_is_online` | Online Status | — | mdi:wifi-check |
| `app_active` | App Active | — | mdi:checkbox-marked-circle |
| `current_time_secs` | Device Time | timestamp | mdi:clock-outline |
| `model_description` | Model | — | mdi:water-well |
| `nickname` | Device Name | — | mdi:label-outline |
| `product_serial_number` | Serial Number | — | mdi:barcode |
| `system_type` | System Type | — | mdi:water-pump |
| `model_display_code` | Model Display Code | — | mdi:identifier |
| `base_software_version` | Base Software Version | — | mdi:application |
| `esp_software_part_number` | ESP Software Part Number | — | mdi:chip |
| `location` | Location | — | mdi:map-marker |

### Water Usage

| API Property | Sensor Name | Unit (COM / EU) | State Class |
|-------------|-------------|-----------------|-------------|
| `current_water_flow_gpm` | Current Water Flow | GPM / L/min | Measurement |
| `gallons_used_today` | Water Used Today | gal / L | Total Increasing |
| `avg_daily_use_gals` | Average Daily Water Usage | gal / L | Measurement |
| `total_outlet_water_gals` | Total Treated Water | gal / L | Total Increasing |
| `peak_water_flow_gpm` | Peak Water Flow | GPM / L/min | Measurement |
| `treated_water_avail_gals` | Available Treated Water | gal / L | Measurement |
| `water_counter_gals` | Water Counter | gal / L | Total Increasing |

### Salt Management

| API Property | Sensor Name | Unit (COM / EU) | State Class |
|-------------|-------------|-----------------|-------------|
| `salt_level_tenths` | Salt Level | % | Measurement |
| `out_of_salt_estimate_days` | Days Until Salt Needed | days | Measurement |
| `avg_salt_per_regen_lbs` | Salt Used per Regeneration | lbs / kg | Measurement |
| `total_salt_use_lbs` | Total Salt Used | lbs / kg | Total Increasing |
| `salt_effic_grains_per_lb` | Salt Efficiency | grains/lb | Measurement |
| `salt_type_enum` | Salt Type | — | — |
| `iron_level_tenths_ppm` | Iron Level | ppm | Measurement |

### System Performance

| API Property | Sensor Name | Unit (COM / EU) | State Class |
|-------------|-------------|-----------------|-------------|
| `capacity_remaining_percent` | Capacity Remaining | % | Measurement |
| `operating_capacity_grains` | Operating Capacity | grains | Measurement |
| `hardness_grains` | Water Hardness | grains | Measurement |
| `rock_removed_since_rech_lbs` | Hardness Removed Since Recharge | lbs / kg | Measurement |
| `daily_avg_rock_removed_lbs` | Average Daily Hardness Removed | lbs / kg | Measurement |
| `total_rock_removed_lbs` | Total Hardness Removed | lbs / kg | Total Increasing |

### Regeneration

| API Property | Sensor Name | Unit | State Class |
|-------------|-------------|------|-------------|
| `regen_status_enum` | Regeneration Status | — | — |
| `days_since_last_regen` | Days Since Last Regeneration | days | Measurement |
| `total_regens` | Total Regenerations | — | Total Increasing |
| `manual_regens` | Manual Regenerations | — | Total Increasing |
| `regen_time_rem_secs` | Regeneration Time Remaining | sec | Measurement |
| `regen_time_secs` | Regeneration Time | sec | Measurement |

### Alerts

All alert sensors return `0` (OK) or non-zero (active).

| API Property | Sensor Name | Icon |
|-------------|-------------|------|
| `low_salt_alert` | Low Salt Alert | mdi:alert-circle |
| `error_code_alert` | Error Code Alert | mdi:alert |
| `error_code` | Error Code | mdi:alert-octagon |
| `flow_monitor_alert` | Flow Monitor Alert | mdi:water-alert |
| `excessive_water_use_alert` | Excessive Water Use Alert | mdi:water-alert |
| `floor_leak_detector_alert` | Leak Detector Alert | mdi:water-alert |
| `service_reminder_alert` | Service Reminder Alert | mdi:tools |
| `system_error` | System Error | mdi:alert |

### System & Connectivity

| API Property | Sensor Name | Unit | State Class |
|-------------|-------------|------|-------------|
| `rf_signal_strength_dbm` | WiFi Signal Strength | dBm | Measurement |
| `rf_signal_bars` | WiFi Signal Quality | — | Measurement |
| `days_in_operation` | Days in Operation | days | Measurement |
| `power_outage_count` | Power Outage Count | — | Total Increasing |
| `service_reminder_months` | Months Until Service | months | Measurement |
| `time_lost_events` | Time Lost Events | — | Total Increasing |
| `tlc_avg_temp_tenths_c` | TLC Average Temperature | °C | Measurement |
| `service_active` | Service Mode Active | — | — |
| `vacation_mode` | Vacation Mode | — | — |

## Additional Sensors

Properties returned by the API that don't have an explicit sensor definition are still created as sensors with auto-generated names (e.g. `avg_daily_dev_day_1_gals` becomes "Avg Daily Dev Day 1 Gals"). These are disabled by default but can be enabled in **Settings > Devices & Services > HydroLink > Entities**.

## Source

Full sensor definitions: [sensor.py](custom_components/hydrolink/sensor.py)
