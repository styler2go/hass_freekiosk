"""FreeKiosk API client."""

from __future__ import annotations

import socket

import aiohttp
import async_timeout

from .const import (
    CONF_HEADER_API_KEY,
    LOGGER,
    REST_ENDPOINT_HEALTH,
    REST_ENDPOINT_SCREENSHOT,
    REST_ENDPOINT_STATUS,
)


class FreeKioskApiClientError(Exception):
    """Base FreeKiosk API error."""


class FreeKioskApiClientAuthenticationError(FreeKioskApiClientError):
    """Authentication failed."""


class FreeKioskApiClientCommunicationError(FreeKioskApiClientError):
    """General communication failure."""


class FreeKioskApiClient:
    """Client for talking to the FreeKiosk REST API."""

    def __init__(
        self,
        base_url: str,
        session: aiohttp.ClientSession,
        api_key: str | None = None,
    ) -> None:
        """Set up client."""
        self._base_url = base_url.rstrip("/")
        self._session = session
        self._api_key = api_key

    async def async_get_status(self) -> dict[str, object]:
        """Return the full /api/status payload."""
        return await self._async_request("GET", REST_ENDPOINT_STATUS)

    async def async_get_health(self) -> dict[str, object]:
        """Return the /api/health payload."""
        return await self._async_request("GET", REST_ENDPOINT_HEALTH)

    async def async_get_screenshot(self) -> bytes:
        """Return the /api/screenshot payload."""
        return await self._async_request_bytes("GET", REST_ENDPOINT_SCREENSHOT)

    async def _async_request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, object]:
        """Make an HTTP request."""
        headers: dict[str, str] = {}
        if self._api_key:
            headers[CONF_HEADER_API_KEY] = self._api_key

        url = f"{self._base_url}{endpoint}"
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=headers or None,
                )
                if response.status in (401, 403):
                    LOGGER.debug(
                        "Received %s from FreeKiosk (%s)",
                        response.status,
                        url,
                    )
                    raise FreeKioskApiClientAuthenticationError
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, socket.gaierror) as err:
            LOGGER.exception("Error talking to FreeKiosk API: %s", err)
            raise FreeKioskApiClientCommunicationError from err
        except TimeoutError as err:
            LOGGER.exception("Timeout fetching FreeKiosk status: %s", err)
            raise FreeKioskApiClientCommunicationError from err

    async def _async_request_bytes(
        self,
        method: str,
        endpoint: str,
    ) -> bytes:
        """Make an HTTP request and return raw bytes."""
        headers: dict[str, str] = {}
        if self._api_key:
            headers[CONF_HEADER_API_KEY] = self._api_key

        url = f"{self._base_url}{endpoint}"
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers or None,
                )
                if response.status in (401, 403):
                    LOGGER.debug(
                        "Received %s from FreeKiosk (%s)",
                        response.status,
                        url,
                    )
                    raise FreeKioskApiClientAuthenticationError
                response.raise_for_status()
                return await response.read()
        except (aiohttp.ClientError, socket.gaierror) as err:
            LOGGER.exception("Error talking to FreeKiosk API: %s", err)
            raise FreeKioskApiClientCommunicationError from err
        except TimeoutError as err:
            LOGGER.exception("Timeout fetching FreeKiosk screenshot: %s", err)
            raise FreeKioskApiClientCommunicationError from err

    async def async_post_command(
        self,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, object]:
        """Send a POST command to FreeKiosk."""
        return await self._async_request("POST", endpoint, data)
