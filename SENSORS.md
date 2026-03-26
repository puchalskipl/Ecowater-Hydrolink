# Sensor Documentation

The integration auto-discovers all properties from the HydroLink API and exposes them as sensors. A typical device provides ~110 properties, of which 38 have explicit definitions and 17 are enabled by default (★).

## Units

For the **hydrolinkhome.eu** region, the API returns `converted_value` in metric units, which the integration uses automatically:

| Measurement | hydrolinkhome.com | hydrolinkhome.eu |
|-------------|-------------------|------------------|
| Volume | Gallons | Liters |
| Flow rate | GPM | L/min |
| Mass | lbs | kg |

## Value Scaling

Some API values are stored in scaled format. The integration converts them automatically:

| Rule | Affected properties | Example |
|------|-------------------|---------|
| From enriched_data | `salt_level_tenths` — reads `enriched_data.water_treatment.salt_level.salt_level_percent` | API raw: 40, enriched: **75%** |
| Divide by 10 | Properties with `_tenths` in name | `iron_level_tenths_ppm`: 30 → 3.0 ppm |
| Divide by 10 | `capacity_remaining_percent`, `average_exhaustion_percent` | 550 → 55.0% |
| Divide by 10 | `total_salt_use_lbs` | 650 → 65.0 lbs / 29.5 kg |
| Divide by 100 | `avg_days_between_regens` | 380 → 3.80 days |
| Divide by 10000 | `avg_salt_per_regen_lbs` | 15000 → 1.50 lbs / 0.68 kg |

## Sensor List

### Basic

| ★ | API Property | Sensor Name | Description | Example Value |
|---|-------------|-------------|-------------|---------------|
| ★ | `_internal_is_online` | Online Status | Whether the device is online | `true` |
| | `model_description` | Model | Device model name | `eVOLUTION 300 BOOST` |
| | `product_serial_number` | Serial Number | Device serial number | `XXXX-XXXXX-XXXX` |

### Water

| ★ | API Property | Sensor Name | Description | Raw | Plugin (EU) |
|---|-------------|-------------|-------------|-----|-------------|
| ★ | `current_water_flow_gpm` | Current Water Flow | Real-time water flow rate | 2.5 gpm | **9.5 L/min** |
| ★ | `gallons_used_today` | Water Used Today | Water consumed today | 25 gal | **95 L** |
| ★ | `avg_daily_use_gals` | Average Daily Water Usage | Rolling average daily consumption | 50 gal | **189 L** |
| ★ | `total_outlet_water_gals` | Total Treated Water | Lifetime treated water volume | 12000 gal | **45 420 L** |
| | `total_untreated_water_gals` | Total Untreated Water | Lifetime untreated water volume | 30 gal | **114 L** |
| | `peak_water_flow_gpm` | Peak Water Flow | Maximum recorded flow rate | 7.5 gpm | **28.4 L/min** |
| | `treated_water_avail_gals` | Available Treated Water | Treated water remaining before regeneration | 120 gal | **454 L** |
| | `water_counter_gals` | Water Counter | Water meter counter | 12000 gal | **45 420 L** |

### Salt

| ★ | API Property | Sensor Name | Description | Raw | Plugin (EU) |
|---|-------------|-------------|-------------|-----|-------------|
| ★ | `salt_level_tenths` | Salt Level | Salt reservoir level (from enriched_data) | 40 | **75%** |
| ★ | `out_of_salt_estimate_days` | Days Until Salt Needed | Estimated days before salt refill needed | 120 | **120 days** |
| ★ | `total_salt_use_lbs` | Total Salt Used | Lifetime salt consumption | 650 → 295 | **29.5 kg** (/10) |
| | `avg_salt_per_regen_lbs` | Salt Used per Regeneration | Average salt per regeneration cycle | 15000 → 6804 | **0.68 kg** (/10000) |

### Performance

| ★ | API Property | Sensor Name | Description | Raw | Plugin |
|---|-------------|-------------|-------------|-----|--------|
| ★ | `capacity_remaining_percent` | Capacity Remaining | Remaining resin capacity before regeneration | 550 | **55.0%** (/10) |
| | `average_exhaustion_percent` | Average Exhaustion | Average resin exhaustion level | 650 | **65.0%** (/10) |

### Regeneration

| ★ | API Property | Sensor Name | Description | Raw | Plugin |
|---|-------------|-------------|-------------|-----|--------|
| ★ | `regen_status_enum` | Regeneration Status | Current regeneration cycle state (0=idle) | 0 | **0** |
| ★ | `days_since_last_regen` | Days Since Last Regeneration | Days elapsed since last regeneration | 3 | **3 days** |
| ★ | `total_regens` | Total Regenerations | Lifetime regeneration count | 52 | **52** |
| | `avg_days_between_regens` | Average Days Between Regenerations | Average interval between regeneration cycles | 380 | **3.80 days** (/100) |
| | `manual_regens` | Manual Regenerations | Manually triggered regeneration count | 2 | **2** |
| | `regen_time_rem_secs` | Regeneration Time Remaining | Time left in current regeneration cycle | 0 | **0 sec** |
| | `current_valve_position_enum` | Valve Position | Current valve position (0=service) | 0 | **0** |

### Alerts

All alert sensors return `0` (OK) or non-zero (active).

| ★ | API Property | Sensor Name | Description | Value |
|---|-------------|-------------|-------------|-------|
| ★ | `low_salt_alert` | Low Salt Alert | Low salt level warning | `0` (OK) |
| ★ | `error_code_alert` | Error Code Alert | System error indicator | `0` (OK) |
| ★ | `excessive_water_use_alert` | Excessive Water Use Alert | Abnormally high water usage | `0` (OK) |
| ★ | `floor_leak_detector_alert` | Leak Detector Alert | Floor leak sensor triggered | `0` (OK) |
| | `error_code` | Error Code | Numeric error code | `0` |
| | `depletion_alert` | Depletion Alert | Resin capacity depleted | `0` (OK) |
| | `flow_monitor_alert` | Flow Monitor Alert | Continuous flow detected | `0` (OK) |
| | `wtd_alert` | Water to Drain Alert | Water-to-drain monitor triggered | `0` (OK) |
| | `service_reminder_alert` | Service Reminder Alert | Scheduled maintenance reminder | `0` (OK) |

### System & Connectivity

| ★ | API Property | Sensor Name | Description | Value |
|---|-------------|-------------|-------------|-------|
| ★ | `rf_signal_strength_dbm` | WiFi Signal Strength | WiFi signal strength | **-55 dBm** |
| | `rf_signal_bars` | WiFi Signal Quality | WiFi signal bars (0–4) | **3** |
| | `wifi_ssid` | WiFi SSID | Connected WiFi network name | `MyNetwork-5G` |
| | `days_in_operation` | Days in Operation | Total days since installation | **210 days** |
| | `power_outage_count` | Power Outage Count | Number of detected power failures | **3** |
| | `time_lost_events` | Time Lost Events | Clock reset events | **1** |
| | `service_reminder_months` | Months Until Service | Months until service due (-1=disabled) | **-1** |
| | `service_active` | Service Mode Active | Whether service mode is enabled | `false` |
| | `base_software_version` | Base Software Version | Controller firmware version | `T3.1 MPC01165-2523` |
| | `esp_software_part_number` | ESP Software Part Number | WiFi module firmware version | `W1.0.0 7396274` |

## Additional Sensors

Properties returned by the API that don't have an explicit sensor definition (~70 technical/config properties) are still created as sensors with auto-generated names. These are disabled by default but can be enabled in **Settings > Devices & Services > HydroLink > Entities**.

## Source

Full sensor definitions: [sensor.py](custom_components/hydrolink/sensor.py)
