from decimal import Decimal
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass
)

from .const import DOMAIN, COORDINATOR_KEY
from .coordinator import BadiCrowdmonitorDataCoordinator, BadiCrowdData

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: BadiCrowdmonitorDataCoordinator = hass.data[DOMAIN][COORDINATOR_KEY]
    current_data: list[BadiCrowdData] = coordinator.data
    _LOGGER.debug(f"Trying to add {current_data}")
    entities = []
    for e in current_data.values():
        entities.append(BadiCrowdEntity(e.id, e.name, coordinator, True))
        entities.append(BadiCrowdEntity(e.id, e.name, coordinator, False))
    async_add_entities(entities)
    
class BadiCrowdEntity(CoordinatorEntity[BadiCrowdmonitorDataCoordinator], SensorEntity):
    _id: str = ""
    _name: str = ""
    _coordinator: BadiCrowdmonitorDataCoordinator
    _taken: bool

    def __init__(self, id: str, name: str, coordinator: BadiCrowdmonitorDataCoordinator, taken:bool):
        self.entity_description = SensorEntityDescription(
            key="badi_{id}",
            name=name,
            state_class=SensorStateClass.MEASUREMENT
        )
        self._id = id
        self._name = name
        self._coordinator = coordinator
        self._taken = taken
        taken_or_free_str = "Spaces Taken" if taken else "Spaces Free" 
        taken_or_free_id = "taken" if taken else "free" 
        self._attr_icon = "mdi:swim" if taken else "mdi:pool"
        self._attr_name = f"{name} {taken_or_free_str}"
        self._attr_unique_id = f"badi-{id}-{taken_or_free_id}"
        self._attr_device_info = DeviceInfo(entry_type=DeviceEntryType.SERVICE, identifiers={(DOMAIN, "badi")})
        _LOGGER.debug(f"Created {id}/{name}/{taken}")

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success
    
    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        await self._coordinator.async_request_refresh()

    @property
    def native_value(self) -> StateType | Decimal:
        if self._coordinator.data is None:
            _LOGGER.debug(f"Returning none for {self}")
            return None
        
        data:BadiCrowdData = self._coordinator.data.get(self._id)
        if data is not None:
            value = data.spaces_taken if self._taken else data.spaces_free
            _LOGGER.debug(f"Value for {self._id}: {value}")
            return value
        else:
            _LOGGER.warn(f"Couldn't find data for ID {self._id}")
        return None