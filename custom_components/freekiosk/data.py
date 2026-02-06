"""Custom types for the FreeKiosk integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from homeassistant.loader import Integration

    from .api import FreeKioskApiClient
    from .coordinator import FreeKioskDataUpdateCoordinator


@dataclass
class FreeKioskData:
    """Data for the FreeKiosk integration."""

    client: FreeKioskApiClient
    coordinator: FreeKioskDataUpdateCoordinator
    integration: Integration


FreeKioskConfigEntry = ConfigEntry[FreeKioskData]
