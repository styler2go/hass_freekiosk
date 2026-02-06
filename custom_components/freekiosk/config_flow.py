"""Config flow for FreeKiosk."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

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
                await self._test_connection(
                    url=user_input[CONF_DEVICE_URL],
                    api_key=user_input.get(CONF_API_KEY),
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
                        CONF_API_KEY: user_input.get(CONF_API_KEY),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVICE_URL,
                        default=(user_input or {}).get(CONF_DEVICE_URL),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.URL,
                            placeholder="http://192.168.1.50:8080",
                        )
                    ),
                    vol.Optional(
                        CONF_API_KEY,
                        default=(user_input or {}).get(CONF_API_KEY),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def _test_connection(self, url: str, api_key: str | None) -> None:
        """Test if we can connect to the FreeKiosk API."""
        client = FreeKioskApiClient(
            base_url=url,
            api_key=api_key,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_status()
