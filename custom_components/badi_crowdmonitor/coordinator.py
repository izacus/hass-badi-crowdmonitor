from dataclasses import dataclass
import json
import logging
import ssl
import websockets

from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

@dataclass
class BadiCrowdData:
    id: str = ""
    name: str = ""
    spaces_taken: int | None = None
    spaces_free: int | None = None

class BadiCrowdmonitorDataCoordinator(DataUpdateCoordinator["BadiCrowdmonitorCoordinator"]):
    """ WSS data retrieval coordinator """

    WSS_URL = "wss://badi-public.crowdmonitor.ch:9591/api"

    def __init__(self, hass: HomeAssistant) -> None:
        update_interval = timedelta(minutes=5)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self) -> dict[str, BadiCrowdData]:
        _LOGGER.info("Updating badi crowd state...")

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            async with websockets.connect(self.WSS_URL, ssl=ctx) as websocket:
                await websocket.send("all")
                response = await websocket.recv()
                _LOGGER.debug(f"Response: {response}")
                json_data = json.loads(response)
                data = {e.get("uid"): BadiCrowdData(e.get("uid"), e.get("name"), to_int(e.get("currentfill")), to_int(e.get("freespace"))) for e in json_data}
                return data
        except:
            raise UpdateFailed("Could not load data")
        
def to_int(val: str) -> int | None:
    try:
        return int(val)
    except ValueError:
        return None
