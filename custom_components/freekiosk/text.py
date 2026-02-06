"""Text entity exposing FreeKiosk WebView URL."""

from __future__ import annotations

from typing import Any

from homeassistant.components.text import TextEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import FreeKioskDataUpdateCoordinator
from .data import FreeKioskConfigEntry
from .entity import FreeKioskEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FreeKioskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the FreeKiosk text entity."""
    async_add_entities([FreeKioskUrlText(entry.runtime_data.coordinator)])


class FreeKioskUrlText(FreeKioskEntity, TextEntity):
    """Text entity that mirrors the kiosk's current URL."""

    _attr_icon = "mdi:web"

    def __init__(self, coordinator: FreeKioskDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = "FreeKiosk WebView URL"

    @property
    def native_value(self) -> str | None:
        """Return the current WebView URL."""
        return self._get_path("webview", "currentUrl")

    async def async_set_value(self, value: str) -> None:
        """Set a new target URL on the kiosk."""
        await self.coordinator.config_entry.runtime_data.client.async_post_command(
            "/api/url",
            {"url": value},
        )
        await self.coordinator.async_request_refresh()
*** End Patch
