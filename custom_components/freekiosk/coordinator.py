"""DataUpdateCoordinator for FreeKiosk."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    FreeKioskApiClientAuthenticationError,
    FreeKioskApiClientError,
)

if TYPE_CHECKING:
    from .data import FreeKioskConfigEntry


class FreeKioskDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator that polls FreeKiosk."""

    config_entry: FreeKioskConfigEntry

    async def _async_update_data(self) -> Any:
        """Fetch latest data."""
        try:
            status = await self.config_entry.runtime_data.client.async_get_status()
            if not isinstance(status, dict):
                return status
            data = status.get("data")
            if not isinstance(data, dict):
                data = {}
            try:
                health = await self.config_entry.runtime_data.client.async_get_health()
            except FreeKioskApiClientError:
                health = None
            if isinstance(health, dict):
                data["health"] = health.get("data", health)
            status["data"] = data
            return status
        except FreeKioskApiClientAuthenticationError as err:
            raise ConfigEntryAuthFailed(err) from err
        except FreeKioskApiClientError as err:
            raise UpdateFailed(err) from err
