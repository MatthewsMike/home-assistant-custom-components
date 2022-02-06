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
    session = async_get_clientsession(hass)
    sensor = NSPowerOutagesSensor(session)
    async_add_entities([sensor], update_before_add=True)


class NSPowerOutagesSensor(Entity):
    """Representation of a NS Power Outage sensor."""

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.attrs: Dict[str, int] = {'Outages': -1, 'AffectedCustomers': -1}
        self._name = "Nova Scotia Power Outages"
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
        """Returns the current state (Online/Offline) of the sensor"""
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, int]:
        """Contains all the sensors states"""
        return self.attrs

    def keys_url(self):
        """Generates URL to load the key (called "directory") to access data from NS Power"""
        self.timestamp = time.time()*1000
        return f"http://outagemap.nspower.ca/resources/data/external/interval_generation_data/metadata.json?_={self.timestamp}"


    def data_url(self):
        """Generates URL to load current data from NS Power"""
        url = f'http://outagemap.nspower.ca/resources/data/external/interval_generation_data/' + \
                f'{self.key}/data.json?_={self.timestamp + 1}'
        return url

    async def fetch_keys(self, session):
        """Returns response body containing keys to access data on subsequent requests"""
        async with session.get(self.keys_url()) as response:
            return await response.text()

    async def fetch_data(self, session):
        """Returns primary data from NS power"""
        async with session.get(self.data_url()) as response:
            return await response.text()

    async def async_update(self):
        """Get latest data and save it to self.attrs for access by Home Assistant"""
        async with self.session as session:
            try:
                _LOGGER.info("Updating Sensor values.")
                keys = await self.fetch_keys(session)
                self.key = json.loads(keys)['directory']
                result = await self.fetch_data(session)
                data = json.loads(result)
                self.attrs['AffectedCustomers'] = int(data['summaryFileData']['total_cust_a']['val'])
                self.attrs['Outages'] = int(data['summaryFileData']['total_outages'])
                self._available = True
                self._state = "Online"
            except:
                self._available = False
                self._state = "Offline"
                _LOGGER.exception("Error retrieving data from NS Power.")

