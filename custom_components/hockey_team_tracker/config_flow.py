import logging
from typing import Any, Dict, Optional

import aiohttp
import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, CONF_PATH, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_CLUB,
    CONF_CLUB_NAME,
    CONF_TEAM,
    CONF_TEAM_NAME,
    CONF_TEAMS,
    DOMAIN,
)
from .HockeyWeerelt import hockeyweerelt

_LOGGER = logging.getLogger(__name__)


class HockeyTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hockey Team Tracker config flow."""

    data: Optional[Dict[str, Any]]

    async def async_step_team(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a team to watch."""
        _LOGGER.info(user_input)
        errors: Dict[str, str] = {}
        team_dict = await self._get_team_dict(self.data[CONF_CLUB])
        if user_input is not None:
            if not errors:
                team_id = team_dict[user_input[CONF_TEAM]]
                self.data[CONF_TEAMS].append(
                    {
                        CONF_TEAM_NAME: user_input[CONF_TEAM],
                        CONF_TEAM: team_id,
                        CONF_NAME: user_input.get(
                            CONF_NAME,
                            f"{self.data[CONF_CLUB_NAME]} {user_input[CONF_TEAM]}",
                        ),
                    }
                )

                if user_input.get("add_another", False):
                    return await self.async_step_team()

                # User is done adding repos, create the config entry.
                return self.async_create_entry(
                    title="Hockey Team Tracker", data=self.data
                )

        return self.async_show_form(
            step_id="team",
            data_schema=await HockeyTrackerConfigFlow._get_team_schema(team_dict),
            errors=errors,
        )

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        self.hockeyWeereltApi = hockeyweerelt.Api(
            session=async_get_clientsession(self.hass)
        )

        errors: Dict[str, str] = {}
        club_dict = await self._get_club_dict()
        if user_input is not None:
            if not errors:
                # Input is valid, set data.

                self.data = {
                    CONF_CLUB: club_dict[user_input[CONF_CLUB]],
                    CONF_CLUB_NAME: user_input[CONF_CLUB],
                }
                self.data[CONF_TEAMS] = []

                return await self.async_step_team()

        return self.async_show_form(
            step_id="user",
            data_schema=await HockeyTrackerConfigFlow._get_club_schema(club_dict),
            errors=errors,
        )

    async def _get_team_dict(self, club: str):
        team_dict = {}
        team_data = await self.hockeyWeereltApi.get_club_teams(club)
        for item in team_data["data"]:
            team_dict[f"{item['short_name']} {item['type']}"] = item["id"]
        return team_dict

    @staticmethod
    async def _get_team_schema(team_dict):
        return vol.Schema(
            {
                vol.Required(CONF_TEAM): vol.In({k: k for k in team_dict}),
                vol.Optional(CONF_NAME): cv.string,
                vol.Optional("add_another"): cv.boolean,
            }
        )

    async def _get_club_dict(self):
        club_data = await self.hockeyWeereltApi.get_clubs()

        club_dict = {}

        for item in club_data["data"]:
            club_dict[item["name"]] = item["id"]

        return club_dict

    @staticmethod
    async def _get_club_schema(club_dict):
        CLUB_SCHEMA = vol.Schema(
            {vol.Required(CONF_CLUB): vol.In({k: k for k in club_dict})}
        )

        return CLUB_SCHEMA
