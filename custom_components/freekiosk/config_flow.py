"""Config flow for FreeKiosk."""

from __future__ import annotations

from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    FreeKioskApiClient,
    FreeKioskApiClientAuthenticationError,
    FreeKioskApiClientCommunicationError,
    FreeKioskApiClientError,
)
from .const import CONF_DEVICE_URL, DOMAIN, LOGGER


class FreeKioskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FreeKiosk."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                api_key = user_input.get(CONF_API_KEY) or None
                await self._test_connection(
                    url=user_input[CONF_DEVICE_URL],
                    api_key=api_key,
                )
            except FreeKioskApiClientAuthenticationError as err:
                LOGGER.debug("Authentication failed: %s", err)
                errors["base"] = "auth"
            except FreeKioskApiClientCommunicationError as err:
                LOGGER.debug("Communication error: %s", err)
                errors["base"] = "connection"
            except FreeKioskApiClientError as err:
                LOGGER.exception("Unexpected API error: %s", err)
                errors["base"] = "unknown"
            else:
                normalized_url = user_input[CONF_DEVICE_URL].rstrip("/")
                unique_id = normalized_url
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_DEVICE_URL],
                    data={
                        CONF_DEVICE_URL: normalized_url,
                        CONF_API_KEY: api_key,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_user_schema(user_input),
            errors=errors,
        )

    async def _test_connection(self, url: str, api_key: str | None) -> None:
        """Test if we can connect to the FreeKiosk API."""
        client = FreeKioskApiClient(
            base_url=url,
            api_key=api_key,
            session=async_get_clientsession(self.hass),
        )
        response = await client.async_get_health()
        if not response.get("success"):
            LOGGER.debug("Health check did not return success: %s", response)
            raise FreeKioskApiClientCommunicationError


def _build_user_schema(user_input: dict[str, Any] | None) -> vol.Schema:
    defaults = user_input or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_DEVICE_URL,
                default=defaults.get(CONF_DEVICE_URL),
            ): cv.string,
            vol.Optional(
                CONF_API_KEY,
                default=defaults.get(CONF_API_KEY, ""),
            ): cv.string,
        }
    )
