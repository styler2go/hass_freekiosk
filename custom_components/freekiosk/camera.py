"""Camera platform for FreeKiosk."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.camera import Camera

from .api import FreeKioskApiClientError
from .const import LOGGER
from .entity import FreeKioskEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FreeKioskDataUpdateCoordinator
    from .data import FreeKioskConfigEntry


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: FreeKioskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the FreeKiosk camera."""
    async_add_entities([FreeKioskScreenshotCamera(entry.runtime_data.coordinator)])


class FreeKioskScreenshotCamera(FreeKioskEntity, Camera):
    """Camera entity that exposes the latest screenshot."""

    _attr_name = "FreeKiosk Screenshot"
    _attr_icon = "mdi:camera"

    def __init__(self, coordinator: FreeKioskDataUpdateCoordinator) -> None:
        """Initialize the camera entity."""
        super().__init__(coordinator, unique_id="screenshot")

    async def async_camera_image(
        self, _width: int | None = None, _height: int | None = None
    ) -> bytes | None:
        """Return a still image response."""
        try:
            return await (
                self.coordinator.config_entry.runtime_data.client.async_get_screenshot()
            )
        except FreeKioskApiClientError as err:
            LOGGER.debug("Unable to fetch screenshot: %s", err)
            return None
