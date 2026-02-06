"""Sensor platform for FreeKiosk."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

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
        key="battery_temperature",
        name="Battery Temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement="°C",
        value_fn=lambda data: data.get("battery", {}).get("temperature"),
    ),
    FreeKioskSensorDescription(
        key="screen_brightness",
        name="Screen Brightness",
        icon="mdi:brightness-5",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("screen", {}).get("brightness"),
    ),
    FreeKioskSensorDescription(
        key="wifi_rssi",
        name="WiFi RSSI",
        icon="mdi:wifi",
        native_unit_of_measurement="dBm",
        value_fn=lambda data: data.get("wifi", {}).get("rssi"),
    ),
    FreeKioskSensorDescription(
        key="storage_available",
        name="Storage Available",
        icon="mdi:harddisk",
        native_unit_of_measurement="MB",
        value_fn=lambda data: data.get("storage", {}).get("availableMB"),
    ),
    FreeKioskSensorDescription(
        key="storage_used_percent",
        name="Storage Used",
        icon="mdi:harddisk-multiple",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("storage", {}).get("usedPercent"),
    ),
    FreeKioskSensorDescription(
        key="memory_available",
        name="Memory Available",
        icon="mdi:memory",
        native_unit_of_measurement="MB",
        value_fn=lambda data: data.get("memory", {}).get("availableMB"),
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
        key="auto_brightness_level",
        name="Automatic Brightness Level",
        icon="mdi:brightness-6",
        native_unit_of_measurement="lx",
        value_fn=lambda data: data.get("autoBrightness", {}).get("currentLightLevel"),
    ),
    FreeKioskSensorDescription(
        key="audio_volume",
        name="Audio Volume",
        icon="mdi:volume-high",
        native_unit_of_measurement="%",
        value_fn=lambda data: data.get("audio", {}).get("volume"),
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
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> Any:
        """Return the current value."""
        return self.entity_description.value_fn(self._get_status())
