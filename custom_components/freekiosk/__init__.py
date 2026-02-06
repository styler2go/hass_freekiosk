"""The FreeKiosk Home Assistant integration."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import FreeKioskApiClient
from .const import (
    CONF_DEVICE_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)
from .coordinator import FreeKioskDataUpdateCoordinator
from .data import FreeKioskConfigEntry, FreeKioskData
from .services import async_setup_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.TEXT,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FreeKioskConfigEntry,
) -> bool:
    """Set up FreeKiosk from a config entry."""
    coordinator = FreeKioskDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    entry.runtime_data = FreeKioskData(
        client=FreeKioskApiClient(
            base_url=entry.data[CONF_DEVICE_URL],
            api_key=entry.data.get(CONF_API_KEY),
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await async_setup_services(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: FreeKioskConfigEntry,
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: FreeKioskConfigEntry,
) -> None:
    """Reload an entry."""
    await hass.config_entries.async_reload(entry.entry_id)
