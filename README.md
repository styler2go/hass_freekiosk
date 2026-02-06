# FreeKiosk

This repository contains the **FreeKiosk** Home Assistant custom integration. It polls the built-in FreeKiosk REST API and exposes the `/api/status` payload as sensors and binary sensors so you can observe the kiosk's battery, screen, connectivity, and device health.

## Features

- UI config flow that accepts a device URL (e.g. `http://192.168.1.50:8080`) and an optional `X-Api-Key` value.
- Aggregates `/api/status` data through a single `DataUpdateCoordinator` and splits the JSON into individual sensors.
- Binary sensors for screen power, charging, Wi-Fi connectivity, kiosk mode, and autoscreen/brightness flags.
- Designed for use with Home Assistant 2025.2.x and later.

## Configuration

1. Install this custom component by placing the `custom_components/freekiosk` directory in your Home Assistant configuration.
2. Restart Home Assistant.
3. Go to Settings → Devices & Services → Add Integration and search for **FreeKiosk**.
4. Provide the HTTP URL pointing to your FreeKiosk device and optionally your API key if authentication is enabled.
5. The integration will immediately poll `/api/status` and create the sensors listed below.

The full FreeKiosk REST API is described in [`REST_API.md`](REST_API.md) if you want to add automations that call other endpoints.

## Entities

The integration generates the following sensors:

- `sensor.freekiosk_battery_level`
- `sensor.freekiosk_battery_temperature`
- `sensor.freekiosk_screen_brightness`
- `sensor.freekiosk_wifi_rssi`
- `sensor.freekiosk_storage_available`
- `sensor.freekiosk_storage_used_percent`
- `sensor.freekiosk_memory_available`
- `sensor.freekiosk_memory_used_percent`
- `sensor.freekiosk_light_level`
- `sensor.freekiosk_proximity`
- `sensor.freekiosk_auto_brightness_level`
- `sensor.freekiosk_audio_volume`

Binary sensors include:

- `binary_sensor.freekiosk_screen_on`
- `binary_sensor.freekiosk_screensaver_active`
- `binary_sensor.freekiosk_battery_charging`
- `binary_sensor.freekiosk_wifi_connected`
- `binary_sensor.freekiosk_autobrightness_enabled`
- `binary_sensor.freekiosk_kiosk_enabled`

## API coverage

- `GET /api/status`
- `POST /api/brightness`
- `POST /api/autoBrightness/enable`
- `POST /api/autoBrightness/disable`
- `POST /api/screen/on`
- `POST /api/screen/off`
- `POST /api/screensaver/on`
- `POST /api/screensaver/off`
- `POST /api/reload`
- `POST /api/url`
- `POST /api/wake`
- `POST /api/tts`
- `POST /api/toast`
- `POST /api/js`
- `POST /api/clearCache`
- `POST /api/app/launch`
- `POST /api/reboot`
- `POST /api/audio/play`
- `POST /api/audio/stop`
- `POST /api/audio/beep`
- `POST /api/remote/{command}`

## Development

Use the provided `scripts/develop` helper to launch Home Assistant with this integration locally. `config/configuration.yaml` is already wired up to log `custom_components.freekiosk` under `logger` for easier debugging.

Automations can use the sensors and binary sensors above, and REST commands/controls are documented in [`REST_API.md`](REST_API.md).
