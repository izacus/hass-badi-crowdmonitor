from homeassistant import config_entries
from .const import DOMAIN


class BadiCrowdmonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, info):
        return self.async_create_entry(title="Badi Crowdmonitor", data={}, options={})