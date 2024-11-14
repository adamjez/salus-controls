"""Hot water pump entity for the Salus Controls device."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback

class HotWaterEntity(SwitchEntity):
    """Representation of a hot water pump."""

    def __init__(self, name, coordinator, client):
        """Initialize the pump switch."""
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