"""Switch platform for FreeKiosk controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .entity import FreeKioskEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FreeKioskDataUpdateCoordinator
    from .data import FreeKioskConfigEntry


def _auto_brightness_payload(data: dict[str, Any]) -> dict[str, Any]:
    settings = data.get("autoBrightness", {}) or {}
    min_value = settings.get("min")
    max_value = settings.get("max")
    if min_value is None:
        min_value = 10
    if max_value is None:
        max_value = 100
    return {"min": min_value, "max": max_value}


@dataclass
class FreeKioskSwitchDescription(SwitchEntityDescription):
    """Describes a FreeKiosk switch."""

    value_fn: Callable[[dict[str, Any]], bool] = lambda _: False  # type: ignore[assignment]
    turn_on_endpoint: str = ""
    turn_off_endpoint: str = ""
    turn_on_payload: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None


SWITCH_DESCRIPTIONS: tuple[FreeKioskSwitchDescription, ...] = (
    FreeKioskSwitchDescription(
        key="screen",
        name="Screen",
        icon="mdi:monitor",
        value_fn=lambda data: data.get("screen", {}).get("on") is True,
        turn_on_endpoint="/api/screen/on",
        turn_off_endpoint="/api/screen/off",
    ),
    FreeKioskSwitchDescription(
        key="screensaver",
        name="Screensaver",
        icon="mdi:power-sleep",
        value_fn=lambda data: data.get("screen", {}).get("screensaverActive") is True,
        turn_on_endpoint="/api/screensaver/on",
        turn_off_endpoint="/api/screensaver/off",
    ),
    FreeKioskSwitchDescription(
        key="auto_brightness",
        name="Auto Brightness",
        icon="mdi:brightness-auto",
        value_fn=lambda data: data.get("autoBrightness", {}).get("enabled") is True,
        turn_on_endpoint="/api/autoBrightness/enable",
        turn_off_endpoint="/api/autoBrightness/disable",
        turn_on_payload=_auto_brightness_payload,
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: FreeKioskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FreeKiosk switches."""
    async_add_entities(
        FreeKioskSwitch(
            coordinator=entry.runtime_data.coordinator,
            entity_description=description,
        )
        for description in SWITCH_DESCRIPTIONS
    )


class FreeKioskSwitch(FreeKioskEntity, SwitchEntity):
    """Switch representing FreeKiosk state."""

    def __init__(
        self,
        coordinator: FreeKioskDataUpdateCoordinator,
        entity_description: FreeKioskSwitchDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, unique_id=f"switch_{entity_description.key}")
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return the current switch state."""
        return bool(self.entity_description.value_fn(self._get_status()))

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        payload = (
            self.entity_description.turn_on_payload(self._get_status())
            if self.entity_description.turn_on_payload
            else None
        )
        await self.coordinator.config_entry.runtime_data.client.async_post_command(
            self.entity_description.turn_on_endpoint,
            payload,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.config_entry.runtime_data.client.async_post_command(
            self.entity_description.turn_off_endpoint,
        )
        await self.coordinator.async_request_refresh()
