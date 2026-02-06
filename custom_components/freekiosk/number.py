"""Number platform for FreeKiosk controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)

from .entity import FreeKioskEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FreeKioskDataUpdateCoordinator
    from .data import FreeKioskConfigEntry


@dataclass
class FreeKioskNumberDescription(NumberEntityDescription):
    """Describes a FreeKiosk number entity."""

    value_fn: Callable[[dict[str, Any]], float | None] = lambda _: None  # type: ignore[assignment]
    set_endpoint: str = ""


NUMBER_DESCRIPTIONS: tuple[FreeKioskNumberDescription, ...] = (
    FreeKioskNumberDescription(
        key="screen_brightness",
        name="Screen Brightness",
        icon="mdi:brightness-5",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement="%",
        mode=NumberMode.SLIDER,
        value_fn=lambda data: data.get("screen", {}).get("brightness"),
        set_endpoint="/api/brightness",
    ),
    FreeKioskNumberDescription(
        key="audio_volume",
        name="Audio Volume",
        icon="mdi:volume-high",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement="%",
        mode=NumberMode.SLIDER,
        value_fn=lambda data: data.get("audio", {}).get("volume"),
        set_endpoint="/api/volume",
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: FreeKioskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FreeKiosk number entities."""
    async_add_entities(
        FreeKioskNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=description,
        )
        for description in NUMBER_DESCRIPTIONS
    )


class FreeKioskNumber(FreeKioskEntity, NumberEntity):
    """Number entity for FreeKiosk controls."""

    def __init__(
        self,
        coordinator: FreeKioskDataUpdateCoordinator,
        entity_description: FreeKioskNumberDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, unique_id=f"number_{entity_description.key}")
        self.entity_description = entity_description

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        value = self.entity_description.value_fn(self._get_status())
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the value on the FreeKiosk device."""
        payload = {"value": round(value)}
        await self.coordinator.config_entry.runtime_data.client.async_post_command(
            self.entity_description.set_endpoint,
            payload,
        )
        await self.coordinator.async_request_refresh()
