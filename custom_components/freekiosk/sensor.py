"""Sensor platform for FreeKiosk."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.entity import EntityCategory

from .entity import FreeKioskEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FreeKioskDataUpdateCoordinator
    from .data import FreeKioskConfigEntry


@dataclass
class FreeKioskSensorDescription(SensorEntityDescription):
    """Describes FreeKiosk sensor."""

    value_fn: Callable[[dict[str, Any]], Any] = lambda _: None  # type: ignore[assignment]


def _wifi_rssi(data: dict[str, Any]) -> Any:
    return data.get("wifi", {}).get("signalStrength")


def _wifi_ip(data: dict[str, Any]) -> Any:
    return data.get("device", {}).get("ip")


SENSOR_DESCRIPTIONS: tuple[FreeKioskSensorDescription, ...] = (
    FreeKioskSensorDescription(
        key="battery_level",
        name="Battery Level",
        icon="mdi:battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("battery", {}).get("level"),
    ),
    FreeKioskSensorDescription(
        key="battery_plugged",
        name="Battery Plugged",
        icon="mdi:power-plug",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("battery", {}).get("plugged"),
    ),
    FreeKioskSensorDescription(
        key="screen_brightness",
        name="Screen Brightness",
        icon="mdi:brightness-5",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("screen", {}).get("brightness"),
    ),
    FreeKioskSensorDescription(
        key="audio_volume",
        name="Audio Volume",
        icon="mdi:volume-high",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("audio", {}).get("volume"),
    ),
    FreeKioskSensorDescription(
        key="device_hostname",
        name="Device Hostname",
        icon="mdi:lan-connect",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("device", {}).get("hostname"),
    ),
    FreeKioskSensorDescription(
        key="device_version",
        name="Device Version",
        icon="mdi:tag",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("device", {}).get("version"),
    ),
    FreeKioskSensorDescription(
        key="wifi_rssi",
        name="WiFi Signal Strength",
        icon="mdi:wifi",
        native_unit_of_measurement="dBm",
        value_fn=_wifi_rssi,
    ),
    FreeKioskSensorDescription(
        key="wifi_signal_level",
        name="WiFi Signal Level",
        icon="mdi:wifi-strength-2",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("wifi", {}).get("signalLevel"),
    ),
    FreeKioskSensorDescription(
        key="wifi_ssid",
        name="WiFi SSID",
        icon="mdi:wifi",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("wifi", {}).get("ssid"),
    ),
    FreeKioskSensorDescription(
        key="wifi_ip",
        name="WiFi IP",
        icon="mdi:ip-network",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_wifi_ip,
    ),
    FreeKioskSensorDescription(
        key="wifi_link_speed",
        name="WiFi Link Speed",
        icon="mdi:speedometer",
        native_unit_of_measurement="Mbps",
        value_fn=lambda data: data.get("wifi", {}).get("linkSpeed"),
    ),
    FreeKioskSensorDescription(
        key="wifi_frequency",
        name="WiFi Frequency",
        icon="mdi:wifi",
        native_unit_of_measurement="MHz",
        value_fn=lambda data: data.get("wifi", {}).get("frequency"),
    ),
    FreeKioskSensorDescription(
        key="rotation_interval",
        name="Rotation Interval",
        icon="mdi:timer",
        native_unit_of_measurement="s",
        value_fn=lambda data: data.get("rotation", {}).get("interval"),
    ),
    FreeKioskSensorDescription(
        key="rotation_current_index",
        name="Rotation Current Index",
        icon="mdi:counter",
        value_fn=lambda data: data.get("rotation", {}).get("currentIndex"),
    ),
    FreeKioskSensorDescription(
        key="auto_brightness_level",
        name="Automatic Brightness Level",
        icon="mdi:brightness-6",
        native_unit_of_measurement="lx",
        value_fn=lambda data: data.get("autoBrightness", {}).get("currentLightLevel"),
    ),
    FreeKioskSensorDescription(
        key="auto_brightness_min",
        name="Auto Brightness Minimum",
        icon="mdi:brightness-6",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("autoBrightness", {}).get("min"),
    ),
    FreeKioskSensorDescription(
        key="auto_brightness_max",
        name="Auto Brightness Maximum",
        icon="mdi:brightness-7",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("autoBrightness", {}).get("max"),
    ),
    FreeKioskSensorDescription(
        key="storage_total",
        name="Storage Total",
        icon="mdi:harddisk",
        native_unit_of_measurement="MB",
        value_fn=lambda data: data.get("storage", {}).get("totalMB"),
    ),
    FreeKioskSensorDescription(
        key="storage_available",
        name="Storage Available",
        icon="mdi:harddisk",
        native_unit_of_measurement="MB",
        value_fn=lambda data: data.get("storage", {}).get("availableMB"),
    ),
    FreeKioskSensorDescription(
        key="storage_used",
        name="Storage Used",
        icon="mdi:harddisk",
        native_unit_of_measurement="MB",
        value_fn=lambda data: data.get("storage", {}).get("usedMB"),
    ),
    FreeKioskSensorDescription(
        key="storage_used_percent",
        name="Storage Used",
        icon="mdi:harddisk-multiple",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("storage", {}).get("usedPercent"),
    ),
    FreeKioskSensorDescription(
        key="memory_total",
        name="Memory Total",
        icon="mdi:memory",
        native_unit_of_measurement="MB",
        value_fn=lambda data: data.get("memory", {}).get("totalMB"),
    ),
    FreeKioskSensorDescription(
        key="memory_available",
        name="Memory Available",
        icon="mdi:memory",
        native_unit_of_measurement="MB",
        value_fn=lambda data: data.get("memory", {}).get("availableMB"),
    ),
    FreeKioskSensorDescription(
        key="memory_used",
        name="Memory Used",
        icon="mdi:memory",
        native_unit_of_measurement="MB",
        value_fn=lambda data: data.get("memory", {}).get("usedMB"),
    ),
    FreeKioskSensorDescription(
        key="memory_used_percent",
        name="Memory Used",
        icon="mdi:chip",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("memory", {}).get("usedPercent"),
    ),
    FreeKioskSensorDescription(
        key="light_level",
        name="Light Level",
        icon="mdi:weather-sunny",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement="lx",
        value_fn=lambda data: data.get("sensors", {}).get("light"),
    ),
    FreeKioskSensorDescription(
        key="proximity",
        name="Proximity",
        icon="mdi:ruler",
        native_unit_of_measurement="cm",
        value_fn=lambda data: data.get("sensors", {}).get("proximity"),
    ),
    FreeKioskSensorDescription(
        key="accelerometer_x",
        name="Accelerometer X",
        icon="mdi:axis-arrow",
        native_unit_of_measurement="m/s^2",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("sensors", {}).get("accelerometer", {}).get("x"),
    ),
    FreeKioskSensorDescription(
        key="accelerometer_y",
        name="Accelerometer Y",
        icon="mdi:axis-arrow",
        native_unit_of_measurement="m/s^2",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("sensors", {}).get("accelerometer", {}).get("y"),
    ),
    FreeKioskSensorDescription(
        key="accelerometer_z",
        name="Accelerometer Z",
        icon="mdi:axis-arrow",
        native_unit_of_measurement="m/s^2",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("sensors", {}).get("accelerometer", {}).get("z"),
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: FreeKioskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FreeKiosk sensors."""
    async_add_entities(
        FreeKioskStatusSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=description,
        )
        for description in SENSOR_DESCRIPTIONS
    )


class FreeKioskStatusSensor(FreeKioskEntity, SensorEntity):
    """Sensor reporting a single FreeKiosk value."""

    def __init__(
        self,
        coordinator: FreeKioskDataUpdateCoordinator,
        entity_description: FreeKioskSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id=f"sensor_{entity_description.key}")
        self.entity_description = entity_description

    @property
    def native_value(self) -> Any:
        """Return the current value."""
        return self.entity_description.value_fn(self._get_status())
