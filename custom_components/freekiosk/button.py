"""Button platform for FreeKiosk controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .entity import FreeKioskEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FreeKioskDataUpdateCoordinator
    from .data import FreeKioskConfigEntry


@dataclass
class FreeKioskButtonDescription(ButtonEntityDescription):
    """Describes a FreeKiosk button."""

    endpoint: str = ""


BUTTON_DESCRIPTIONS: tuple[FreeKioskButtonDescription, ...] = (
    FreeKioskButtonDescription(
        key="reload",
        name="Reload",
        icon="mdi:reload",
        endpoint="/api/reload",
    ),
    FreeKioskButtonDescription(
        key="wake",
        name="Wake",
        icon="mdi:power",
        endpoint="/api/wake",
    ),
    FreeKioskButtonDescription(
        key="clear_cache",
        name="Clear Cache",
        icon="mdi:cached",
        endpoint="/api/clearCache",
    ),
    FreeKioskButtonDescription(
        key="beep",
        name="Beep",
        icon="mdi:bell-ring",
        endpoint="/api/audio/beep",
    ),
    FreeKioskButtonDescription(
        key="stop_audio",
        name="Stop Audio",
        icon="mdi:stop",
        endpoint="/api/audio/stop",
    ),
    FreeKioskButtonDescription(
        key="reboot",
        name="Reboot",
        icon="mdi:restart",
        endpoint="/api/reboot",
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: FreeKioskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FreeKiosk buttons."""
    async_add_entities(
        FreeKioskButton(
            coordinator=entry.runtime_data.coordinator,
            entity_description=description,
        )
        for description in BUTTON_DESCRIPTIONS
    )


class FreeKioskButton(FreeKioskEntity, ButtonEntity):
    """Button entity for FreeKiosk commands."""

    def __init__(
        self,
        coordinator: FreeKioskDataUpdateCoordinator,
        entity_description: FreeKioskButtonDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, unique_id=f"button_{entity_description.key}")
        self.entity_description = entity_description

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.config_entry.runtime_data.client.async_post_command(
            self.entity_description.endpoint,
        )
        await self.coordinator.async_request_refresh()
