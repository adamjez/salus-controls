"""Hot water pump entity for the Salus Controls device."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback

from custom_components.salus_controls.const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Salus switches from a config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(HotWaterEntity("Hot Water Valve", coordinator, coordinator.get_client))

class HotWaterEntity(SwitchEntity):
    """Representation of a hot water."""

    def __init__(self, name, coordinator, client):
        """Initialize the switch."""
        self._name = name
        self._coordinator = coordinator
        self._client = client
        self._is_on = None
    
    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._client.set_hot_water_mode(True)
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._client.set_hot_water_mode(False)
        await self._coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._is_on = self._coordinator.data.hot_water_enabled
        self.async_write_ha_state()