"""Service helpers for controlling FreeKiosk."""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import CONF_DEVICE_URL, DOMAIN, LOGGER

try:
    from homeassistant.const import CONF_ENTRY_ID
except ImportError:  # pragma: no cover - compatibility fallback
    CONF_ENTRY_ID = "entry_id"

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from homeassistant.core import HomeAssistant, ServiceCall

    from .api import FreeKioskApiClient
    from .data import FreeKioskConfigEntry


@dataclass
class _ServiceDefinition:
    endpoint: str | Callable[[ServiceCall], str]
    payload: Callable[[ServiceCall], dict[str, Any] | None] | None = None
    schema_extra: Mapping[str, Any] | None = None


REMOTE_COMMANDS = (
    "up",
    "down",
    "left",
    "right",
    "select",
    "back",
    "home",
    "menu",
    "playpause",
)


SERVICES: dict[str, _ServiceDefinition] = {
    "screen_on": _ServiceDefinition(endpoint="/api/screen/on"),
    "screen_off": _ServiceDefinition(endpoint="/api/screen/off"),
    "screensaver_on": _ServiceDefinition(endpoint="/api/screensaver/on"),
    "screensaver_off": _ServiceDefinition(endpoint="/api/screensaver/off"),
    "reload": _ServiceDefinition(endpoint="/api/reload"),
    "wake": _ServiceDefinition(endpoint="/api/wake"),
    "clear_cache": _ServiceDefinition(endpoint="/api/clearCache"),
    "reboot": _ServiceDefinition(endpoint="/api/reboot"),
    "set_brightness": _ServiceDefinition(
        endpoint="/api/brightness",
        payload=lambda call: {"value": call.data["value"]},
        schema_extra={
            vol.Required("value"): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        },
    ),
    "set_volume": _ServiceDefinition(
        endpoint="/api/volume",
        payload=lambda call: {"value": call.data["value"]},
        schema_extra={
            vol.Required("value"): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        },
    ),
    "navigate_url": _ServiceDefinition(
        endpoint="/api/url",
        payload=lambda call: {"url": call.data["url"]},
        schema_extra={vol.Required("url"): cv.string},
    ),
    "tts": _ServiceDefinition(
        endpoint="/api/tts",
        payload=lambda call: {"text": call.data["text"]},
        schema_extra={vol.Required("text"): cv.string},
    ),
    "toast": _ServiceDefinition(
        endpoint="/api/toast",
        payload=lambda call: {"text": call.data["text"]},
        schema_extra={vol.Required("text"): cv.string},
    ),
    "execute_js": _ServiceDefinition(
        endpoint="/api/js",
        payload=lambda call: {"code": call.data["code"]},
        schema_extra={vol.Required("code"): cv.string},
    ),
    "launch_app": _ServiceDefinition(
        endpoint="/api/app/launch",
        payload=lambda call: {"package": call.data["package"]},
        schema_extra={vol.Required("package"): cv.string},
    ),
    "play_audio": _ServiceDefinition(
        endpoint="/api/audio/play",
        payload=lambda call: _build_audio_payload(call),
        schema_extra={
            vol.Required("url"): cv.string,
            vol.Optional("loop"): vol.Boolean,
            vol.Optional("volume"): vol.All(cv.positive_int, vol.Range(min=0, max=100)),
        },
    ),
    "stop_audio": _ServiceDefinition(endpoint="/api/audio/stop"),
    "beep": _ServiceDefinition(endpoint="/api/audio/beep"),
    "enable_auto_brightness": _ServiceDefinition(
        endpoint="/api/autoBrightness/enable",
        payload=lambda call: {
            "min": call.data.get("min", 10),
            "max": call.data.get("max", 100),
        },
        schema_extra={
            vol.Optional("min", default=10): vol.All(
                vol.Coerce(int),
                vol.Range(min=0, max=100),
            ),
            vol.Optional("max", default=100): vol.All(
                vol.Coerce(int),
                vol.Range(min=0, max=100),
            ),
        },
    ),
    "disable_auto_brightness": _ServiceDefinition(
        endpoint="/api/autoBrightness/disable"
    ),
    "remote_command": _ServiceDefinition(
        endpoint=lambda call: f"/api/remote/{call.data['command']}",
        schema_extra={vol.Required("command"): vol.In(REMOTE_COMMANDS)},
    ),
}


def _build_audio_payload(call: ServiceCall) -> dict[str, Any]:
    payload: dict[str, Any] = {"url": call.data["url"]}
    loop = call.data.get("loop")
    if loop is not None:
        payload["loop"] = loop
    volume = call.data.get("volume")
    if volume is not None:
        payload["volume"] = volume
    return payload


_SERVICES_REGISTERED_KEY = "services_registered"


def _ensure_target_provided(value: dict[str, Any]) -> dict[str, Any]:
    if value.get(CONF_ENTRY_ID) or value.get(CONF_DEVICE_URL):
        return value
    msg = "Must specify entry_id or device_url"
    raise vol.Invalid(msg)


def _create_schema(extra: Mapping[str, Any] | None) -> vol.Schema:
    schema_dict: dict[str, Any] = {
        vol.Optional(CONF_ENTRY_ID): cv.string,
        vol.Optional(CONF_DEVICE_URL): cv.string,
    }
    if extra:
        schema_dict.update(extra)
    return vol.Schema(vol.All(schema_dict, _ensure_target_provided))


def _find_entry(hass: HomeAssistant, call: ServiceCall) -> FreeKioskConfigEntry | None:
    entry_id = call.data.get(CONF_ENTRY_ID)
    if entry_id:
        return hass.config_entries.async_get_entry(entry_id)
    device_url = call.data.get(CONF_DEVICE_URL)
    if not device_url:
        return None
    normalized_url = device_url.rstrip("/")
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_DEVICE_URL) == normalized_url:
            return entry
    return None


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register FreeKiosk control services."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(_SERVICES_REGISTERED_KEY):
        return

    for service_name, definition in SERVICES.items():
        hass.services.async_register(
            DOMAIN,
            service_name,
            functools.partial(_async_handle_service, definition),
            schema=_create_schema(definition.schema_extra),
        )

    domain_data[_SERVICES_REGISTERED_KEY] = True


async def _async_handle_service(
    service_def: _ServiceDefinition, hass: HomeAssistant, call: ServiceCall
) -> None:
    """Handle an individual FreeKiosk service call."""
    entry = _find_entry(hass, call)
    if not entry or entry.state != ConfigEntryState.LOADED:
        msg = "FreeKiosk entry not available"
        raise HomeAssistantError(msg)

    client: FreeKioskApiClient = entry.runtime_data.client
    endpoint = (
        service_def.endpoint(call)
        if callable(service_def.endpoint)
        else service_def.endpoint
    )
    payload = service_def.payload(call) if service_def.payload else None
    await client.async_post_command(endpoint, payload)
    await entry.runtime_data.coordinator.async_request_refresh()


# Logging stub for coverage
LOGGER.debug("FreeKiosk services module loaded")
