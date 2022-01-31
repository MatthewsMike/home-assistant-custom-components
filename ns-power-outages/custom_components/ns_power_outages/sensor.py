import json
import time
from datetime import datetime, timezone, timedelta
import logging
from typing import Callable, Dict, Optional


from homeassistant.components.sensor import PLATFORM_SCHEMA

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
    }
)
_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(minutes=15)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.info("Custom Sensor async_setup_platform called")
    session = async_get_clientsession(hass)
    sensor = NSPowerOutageSensor(session)
    async_add_entities([sensor], update_before_add=True)


class NSPowerOutageSensor(Entity):
    """Representation of a NS Power Outage sensor."""

    def __init__(self, session):
        super().__init__()
        _LOGGER.info("Custom Sensor Initializing")
        self.session = session
        self.attrs: Dict[str, int] = {'Outages': -1, 'AffectedCustomers': -1}
        self._name = "ns_power_outage"
        self._state = "Online"
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        #TODO is this required?
        return self._name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, int]:
        return self.attrs

    def current_url(self):
        """Generates URL to load current data from NS Power"""
        url = f'http://outagemap.nspower.ca/resources/data/external/interval_generation_data/' + \
                f'{datetime.now(timezone.utc).strftime("%Y_%m_%d_%H_%M_00")}/data.json?_=' + \
                str(int(time.time()*1000))
        return url

    async def fetch(self, session):
        async with session.get(self.current_url()) as response:
            return await response.text()


    async def async_update(self):
        async with self.session as session:
            try:
                _LOGGER.info("Updating Sensor values.")
                result = await self.fetch(session)
                data = json.loads(result)
                self.attrs['AffectedCustomers'] = int(data['summaryFileData']['total_cust_a']['val'])
                self.attrs['Outages'] = int(data['summaryFileData']['total_outages'])
                self._available = True
            except:
                self._available = False
                self._state = "Offline"
                _LOGGER.exception("Error retrieving data from NS Power.")

