"""Constants for the FreeKiosk integration."""

from logging import Logger, getLogger

from homeassistant.const import CONF_URL

LOGGER: Logger = getLogger(__package__)

DOMAIN = "freekiosk"
ATTRIBUTION = "Data provided by FreeKiosk."
DEFAULT_SCAN_INTERVAL = 30
REST_ENDPOINT_STATUS = "/api/status"
REST_ENDPOINT_HEALTH = "/api/health"
REST_ENDPOINT_SCREENSHOT = "/api/screenshot"
CONF_DEVICE_URL = CONF_URL
CONF_HEADER_API_KEY = "X-Api-Key"
