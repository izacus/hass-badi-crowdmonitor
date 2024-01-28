"""The Badi Crowdmonitor integration."""
from __future__ import annotations

import logging

from random import randrange
from homeassistant.config_entries import ConfigEntry

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, COORDINATOR_KEY
from .coordinator import BadiCrowdmonitorDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up Badi Crowdmonitor from a config entry."""
    coordinator = BadiCrowdmonitorDataCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][COORDINATOR_KEY] = coordinator
    await hass.config_entries.async_forward_entry_setup(config, Platform.SENSOR)
    _LOGGER.debug("Setup complete.")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(COORDINATOR_KEY)
    return unload_ok