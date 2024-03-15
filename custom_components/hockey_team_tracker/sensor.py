from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

from .const import CONF_COMPETITION, CONF_TEAM, CONF_TEAMS, DOMAIN
from .HockeyWeerelt import hockeyweerelt

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=10)

TEAM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TEAM): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_COMPETITION): cv.string,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_TEAMS): vol.All(cv.ensure_list, [TEAM_SCHEMA]),
    }
)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    # Update our config to include new repos and remove those that have been removed.
    if config_entry.options:
        config.update(config_entry.options)
    session = async_get_clientsession(hass)
    hockeyweereltapi = hockeyweerelt.Api(session)
    sensors = [
        HockeyTeamTrackerSensor(hockeyweereltapi, team) for team in config[CONF_TEAMS]
    ]
    async_add_entities(sensors, update_before_add=True)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    hockeyweereltapi = hockeyweerelt.Api(session)
    sensors = [
        HockeyTeamTrackerSensor(hockeyweereltapi, team) for team in config[CONF_TEAMS]
    ]
    async_add_entities(sensors, update_before_add=True)


class HockeyTeamTrackerSensor(Entity):
    """Representation of a Hockey Team Tracker sensor."""

    def __init__(self, hockeyweereltapi: hockeyweerelt.Api, team: dict[str, str]):
        super().__init__()
        self.hockeyweereltapi = hockeyweereltapi
        self.team = team[CONF_TEAM]
        self.attrs: dict[str, Any] = {CONF_TEAM: self.team}
        self._name = team[CONF_NAME]
        self._competition = team.get(CONF_COMPETITION, None)
        self._id = self.team
        if self._competition is not None:
            self._id += self._competition
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._id

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self.attrs

    async def async_update(self) -> None:
        """Update all sensors."""
        try:
            match_data = await self.hockeyweereltapi.get_next_team_match(
                self.team, self._competition
            )
            self.attrs = match_data["data"][0]

            self._state = "OK"
            self._available = True
        except Exception:
            self._available = False
            _LOGGER.exception(
                "Error retrieving data from HockeyWeerelt for sensor %s", self.name
            )
