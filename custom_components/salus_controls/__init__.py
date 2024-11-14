"""Support for Salus Controls iT 500 device."""


from .state import State
from .web_client import WebClient
from .thermostat_entity import ThermostatEntity
from .client import Client
import logging

from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.components.climate import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    Platform,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_ID
)

import voluptuous as vol

from . import simulator
from . import (
    ThermostatEntity,
    Client,
    WebClient,
    HotWaterEntity,
)

from .const import DOMAIN
from .coordinator import SalusCoordinator

CONF_SIMULATOR = 'simulator'

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

def create_client_from(config) -> Client:
    """Creates a client object based on the specified configuration"""

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    device_id = config.get(CONF_ID)
    enable_simulator = config.get(CONF_SIMULATOR)

    if enable_simulator:
        _LOGGER.info('Registering Salus Thermostat client simulator...')

        return Client(simulator.WebClient(), simulator.TemperatureClient())
    else:
        web_client = WebClient(username, password, device_id)

        return web_client
