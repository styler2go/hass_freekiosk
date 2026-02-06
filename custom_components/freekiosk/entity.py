"""Base entity for FreeKiosk."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_DEVICE_URL, DOMAIN
from .coordinator import FreeKioskDataUpdateCoordinator


class FreeKioskEntity(CoordinatorEntity[FreeKioskDataUpdateCoordinator]):
    """Entity representing the FreeKiosk device data."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: FreeKioskDataUpdateCoordinator,
        unique_id: str | None = None,
    ) -> None:
        """Initialize base entity."""
        super().__init__(coordinator)
        if unique_id:
            self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{unique_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=coordinator.config_entry.data.get(CONF_DEVICE_URL),
            manufacturer="FreeKiosk",
        )

    def _get_status(self) -> dict[str, Any]:
        """Return the nested data payload."""
        return self.coordinator.data.get("data", {}) or {}

    def _get_path(self, *path: str, default: Any = None) -> Any:
        """Safely traverse nested status data."""
        result: Any = self._get_status()
        for segment in path:
            if not isinstance(result, dict):
                return default
            result = result.get(segment, default)
            if result is default:
                return default
        return result
