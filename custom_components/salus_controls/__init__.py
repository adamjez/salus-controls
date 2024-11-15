"""Support for Salus Controls iT 500 device."""


import logging

from homeassistant.const import (
    Platform,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_ID
)

from .web_client import WebClient
from .thermostat_entity import ThermostatEntity
from .hot_water_entity import HotWaterEntity
from .const import DOMAIN
from .coordinator import SalusCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [
    Platform.CLIMATE,
    Platform.SWITCH
]

async def async_setup_entry(hass, entry) -> bool:
    """Set up components from a config entry."""
    hass.data[DOMAIN] = {}
    if entry.data[CONF_USERNAME]:
        client = create_client_from(entry.data)
        name = entry.data[CONF_ID]

        # assuming API object stored here by __init__.py
        coordinator = SalusCoordinator(hass, client)
        # Fetch initial data so we have data when entities subscribe
        #
        # If the refresh fails, async_config_entry_first_refresh will
        # raise ConfigEntryNotReady and setup will try again later
        #
        # If you do not want to retry setup on failure, use
        # coordinator.async_refresh() instead
        #
        await coordinator.async_config_entry_first_refresh()

        await hass.async_add_entities(
            [ThermostatEntity(name, coordinator, client), HotWaterEntity(name, coordinator, client)],
            update_before_add=True
        )

    return True

def create_client_from(config) -> WebClient:
    """Creates a client object based on the specified configuration"""

    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    device_id = config[CONF_ID]

    _LOGGER.info("Creating Salus web client %s", config)

    return WebClient(username, password, device_id)
