"""Binary sensors for FreeKiosk."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import FreeKioskEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FreeKioskDataUpdateCoordinator
    from .data import FreeKioskConfigEntry


@dataclass
class FreeKioskBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a FreeKiosk binary sensor."""

    value_fn: Callable[[dict[str, Any]], bool] = lambda _: False  # type: ignore[assignment]


BINARY_SENSOR_DESCRIPTIONS: tuple[FreeKioskBinarySensorDescription, ...] = (
    FreeKioskBinarySensorDescription(
        key="screen_on",
        name="Screen On",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: data.get("screen", {}).get("on") is True,
    ),
    FreeKioskBinarySensorDescription(
        key="screensaver_active",
        name="Screensaver Active",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda data: data.get("screen", {}).get("screensaverActive") is True,
    ),
    FreeKioskBinarySensorDescription(
        key="battery_charging",
        name="Battery Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda data: data.get("battery", {}).get("charging") is True,
    ),
    FreeKioskBinarySensorDescription(
        key="wifi_connected",
        name="WiFi Connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data: data.get("wifi", {}).get("connected") is True,
    ),
    FreeKioskBinarySensorDescription(
        key="autobrightness_enabled",
        name="Auto Brightness Enabled",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data: data.get("autoBrightness", {}).get("enabled") is True,
    ),
    FreeKioskBinarySensorDescription(
        key="kiosk_enabled",
        name="Kiosk Mode Enabled",
        device_class=BinarySensorDeviceClass.SAFETY,
        value_fn=lambda data: data.get("kiosk", {}).get("enabled") is True,
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: FreeKioskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FreeKiosk binary sensors."""
    async_add_entities(
        FreeKioskStatusBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=description,
        )
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class FreeKioskStatusBinarySensor(FreeKioskEntity, BinarySensorEntity):
    """Binary sensor representing FreeKiosk boolean state."""

    def __init__(
        self,
        coordinator: FreeKioskDataUpdateCoordinator,
        entity_description: FreeKioskBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return the current state."""
        return bool(self.entity_description.value_fn(self._get_status()))
