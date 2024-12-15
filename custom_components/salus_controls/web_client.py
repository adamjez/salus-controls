"""
Adds support for the Salus Thermostat units.
"""
import time
import logging
import re
import json
import aiohttp

from homeassistant.components.climate.const import (
    HVACMode,
    HVACAction,
)

from homeassistant.helpers.update_coordinator import (
    UpdateFailed,
)

from .state import State
from .const import (
    MAX_TOKEN_AGE_SECONDS,
    URL_GET_DATA,
    URL_GET_TOKEN,
    URL_LOGIN,
    URL_SET_DATA
)

_LOGGER = logging.getLogger(__name__)


class WebClient:
    """Adapter around Salus IT500 web application."""

    def __init__(self, username: str, password: str, device_id: str):
        """Initialize the client."""
        self._username = username
        self._password = password
        self._id = device_id
        self._token = None
        self._token_retrieved_at = None

    async def set_temperature(self, temperature: float) -> None:
        """Set new target temperature, via URL commands."""

        _LOGGER.info("Setting the temperature to %.1f...", temperature)

        options = {"tempUnit": "0", "current_tempZ1_set": "1",
                   "current_tempZ1": temperature}
        data = await self.set_data(options)

        if 'retCode' in data:
            _LOGGER.info("Sucessfully set temperature to %.1f", temperature)
        elif 'errorMsg' in data:
            raise UpdateFailed(f"Server returned: {data["errorMsg"]}")
        else:
            raise UpdateFailed("Server returned unknown error")

    async def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode, via URL commands."""

        _LOGGER.info("Setting the HVAC mode to %s...", hvac_mode)

        auto = "1"
        if hvac_mode == HVACMode.OFF:
            auto = "1"
        elif hvac_mode == HVACMode.HEAT:
            auto = "0"

        options = {"auto": auto, "auto_setZ1": "1"}
        data = await self.set_data(options)

        if data == "1":
            _LOGGER.info("Sucessfully set the HVAC mode to %s", hvac_mode)
        else:
            raise UpdateFailed("Could not set the HVAC mode")

    async def set_hot_water_mode(self, enabled: bool) -> None:
        """Set HVAC mode, via URL commands."""

        _LOGGER.info("Setting the hot water mode to %s...", str(enabled))

        options = {"hwmode_cont": "1"} if enabled else {"hwmode_off": "1"}

        data = await self.set_data(options)

        if data == "2" or data == "3":
            _LOGGER.info(
                "Sucessfully set the hot water mode to %s", str(enabled))
        else:
            raise UpdateFailed("Could not set the hot water mode")

    async def obtain_token(self, session: aiohttp.ClientSession) -> str:
        """Gets the existing session token of the thermostat or retrieves a new one if expired."""

        if self._token is None:
            _LOGGER.info("Retrieving token for the first time this session...")
            await self.get_token(session)
            return self._token

        if self._token_retrieved_at > time.time() - MAX_TOKEN_AGE_SECONDS:
            _LOGGER.debug("Using cached token...")
            return self._token

        _LOGGER.info("Token has expired, getting new one...")
        await self.get_token(session)
        return self._token

    async def get_token(self, session: aiohttp.ClientSession) -> None:
        """Get the Session Token of the Thermostat."""

        _LOGGER.info("Getting token from Salus Gateway...")

        payload = {
            "IDemail": self._username,
            "password": self._password,
            "login": "Login",
            "keep_logged_in": "1"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            await session.post(URL_LOGIN, data=payload, headers=headers)
            params = {"devId": self._id}
            token_response = await session.get(URL_GET_TOKEN, params=params)
            body = await token_response.text()
            result = re.search(
                '<input id="token" type="hidden" value="(.*)" />', body)
            _LOGGER.info("Sucessfully retrieved token")
            self._token = result.group(1)
            self._token_retrieved_at = time.time()
        except Exception as err:
            self._token = None
            self._token_retrieved_at = None
            _LOGGER.error("Error getting the session token: %s", str(err))

    async def get_state(self) -> dict:
        """Retrieves the raw state from the Salus gateway"""

        _LOGGER.debug("Retrieving the device state...")

        async with aiohttp.ClientSession() as session:
            token = await self.obtain_token(session)

            params = {"devId": self._id, "token": token,
                      "&_": str(int(round(time.time() * 1000)))}
            try:
                r = await session.get(url=URL_GET_DATA, params=params)
                if not r:
                    _LOGGER.error("Could not get the data")
                    return None
            except BaseException as err:
                _LOGGER.error(
                    "Error Getting the data from Salus. Check the connection to salus-it500.com.")
                raise UpdateFailed(
                    f"Error during communication with the API: {err}")

            body = await r.text()
            _LOGGER.debug("Sucessfully retrieved the device state: %s", body)
            data = json.loads(body)

            return WebClient.convert_to_state(data)

    async def set_data(self, options: dict) -> dict:
        """Send POST request with token"""

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with aiohttp.ClientSession() as session:
            token = await self.obtain_token(session)

            payload = {
                **options,
                "token": token,
                "devId": self._id}

            try:
                response = await session.post(URL_SET_DATA, data=payload, headers=headers)
                if not response:
                    _LOGGER.error("Could not get data from Salus.")
                    return None
            except BaseException as err:
                _LOGGER.error(
                    "Error during communication with Salus.")
                raise UpdateFailed(
                    f"Error during communication with the API: {err}")

            body = await response.text()
            _LOGGER.debug(
                "Sucessfully retrieved response from action: %s", body)
            data = json.loads(body)
            return data

    @classmethod
    def convert_to_state(cls, data: dict) -> State:
        """Converts the data payload to a state object"""
        state = State()
        state.target_temperature = float(data["CH1currentSetPoint"])
        state.current_temperature = float(data["CH1currentRoomTemp"])
        state.frost = float(data["frost"])

        status = data["CH1heatOnOffStatus"]
        if status == "1":
            state.action = HVACAction.HEATING
        else:
            state.action = HVACAction.IDLE

        heat_on_off = data["CH1heatOnOff"]

        state.mode = HVACMode.OFF if heat_on_off == "1" else HVACMode.HEAT
        state.hot_water_enabled = False if data["HWonOffStatus"] == "0" else True

        return state
