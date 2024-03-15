"""Config flow for Hockey Team Tracker."""

import logging
from typing import Any, Dict, Optional  # noqa: UP035

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_ADD_ANOTHER,
    CONF_CLUB,
    CONF_CLUB_NAME,
    CONF_COMPETITION,
    CONF_COMPETITION_NAME,
    CONF_SELECT_COMP,
    CONF_TEAM,
    CONF_TEAM_NAME,
    CONF_TEAMS,
    DOMAIN,
)
from .HockeyWeerelt import hockeyweerelt

_LOGGER = logging.getLogger(__name__)


def _get_club_schema(club_list):
    CLUB_SCHEMA = vol.Schema({vol.Required(CONF_CLUB_NAME): vol.In(club_list)})

    return CLUB_SCHEMA


def _get_team_schema(team_list):
    TEAM_SCHEMA = vol.Schema(
        {
            vol.Required(CONF_TEAM_NAME): vol.In(team_list),
            vol.Optional(CONF_NAME): cv.string,
            vol.Optional(CONF_SELECT_COMP): cv.boolean,
            vol.Optional(CONF_ADD_ANOTHER): cv.boolean,
        }
    )
    return TEAM_SCHEMA


def _get_competition_schema(competition_list):
    COMPETITION_SCHEMA = vol.Schema(
        {vol.Optional(CONF_COMPETITION_NAME): vol.In(competition_list)}
    )
    return COMPETITION_SCHEMA


class HockeyTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hockey Team Tracker config flow."""

    def __init__(self) -> None:
        """Constructor to setup variables."""
        self.data = {}
        self.extra_data = {}
        self.hockeyweerelt_api = None

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface. Used for selecting the club."""

        # Initialize api
        self.hockeyweerelt_api = hockeyweerelt.Api(
            session=async_get_clientsession(self.hass)
        )

        club_dict, club_list = await self.__get_club_dict()

        if user_input is not None:
            club_name = user_input[CONF_CLUB_NAME]
            self.data[CONF_TEAMS] = []
            self.extra_data[CONF_CLUB] = club_dict[club_name]
            self.extra_data[CONF_CLUB_NAME] = club_name

            return await self.async_step_team()

        return self.async_show_form(
            step_id="user",
            data_schema=_get_club_schema(club_list),
        )

    async def async_step_team(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a team to watch."""

        team_dict, team_list = await self.__get_team_dict(self.extra_data[CONF_CLUB])

        if user_input is not None:
            team_name = user_input[CONF_TEAM_NAME]
            team_id = team_dict[team_name]

            sensor_name = user_input.get(
                CONF_NAME,
                f"{self.extra_data[CONF_CLUB_NAME]} {team_name}",
            )

            team = {CONF_TEAM: team_id, CONF_NAME: sensor_name}

            self.data[CONF_TEAMS].append(team)

            self.extra_data[CONF_ADD_ANOTHER] = user_input.get(CONF_ADD_ANOTHER, False)

            if user_input.get(CONF_SELECT_COMP, False):
                return await self.async_step_competition()
            # Add another is checked
            if self.extra_data[CONF_ADD_ANOTHER]:
                return await self.async_step_team()

            # User is done adding teams and didn't select a competition, create the config entry.
            return self.async_create_entry(title="Hockey Team Tracker", data=self.data)

        return self.async_show_form(
            step_id="team",
            data_schema=_get_team_schema(team_list),
        )

    async def async_step_competition(self, user_input: Optional[Dict[str, Any]] = None):
        """Third optional step in config flow to add a competition to watch for the team."""
        errors: Dict[str, str] = {}
        competition_dict, competition_list = await self.__get_competition_dict(
            self.data[CONF_TEAMS][-1][CONF_TEAM]
        )
        if not competition_list:
            errors["base"] = "empty_list"

        if user_input is not None:
            if user_input.get(CONF_COMPETITION_NAME):
                competition_name = user_input[CONF_COMPETITION_NAME]
                competition_id = competition_dict[competition_name]

                self.data[CONF_TEAMS][-1][CONF_COMPETITION] = competition_id

            # Add another was checked in previous step
            if self.extra_data[CONF_ADD_ANOTHER]:
                return await self.async_step_team()

            # User is done adding teams and selected a competition, create the config entry.
            return self.async_create_entry(title="Hockey Team Tracker", data=self.data)

        return self.async_show_form(
            step_id="competition",
            data_schema=_get_competition_schema(competition_list),
            errors=errors,
        )

    async def __get_club_dict(self):
        club_data = await self.hockeyweerelt_api.get_clubs()

        club_dict = {}
        club_list = []

        for club in club_data["data"]:
            club_name = club["name"]
            club_dict[club_name] = club["id"]
            club_list.append(club_name)

        return club_dict, club_list

    async def __get_team_dict(self, club_id):
        team_data = await self.hockeyweerelt_api.get_club_teams(club_id)

        team_dict = {}
        team_list = []

        for team in team_data["data"]:
            team_name = f"{team['short_name']} {team['type']}"
            team_dict[team_name] = team["id"]
            team_list.append(team_name)

        return team_dict, team_list

    async def __get_competition_dict(self, team_id):
        competition_data = await self.hockeyweerelt_api.get_team_info(team_id)

        competition_dict = {}
        competition_list = []

        for competition in competition_data["data"]["competitions"]:
            competition_name = competition["name"]
            competition_dict[competition_name] = competition["id"]
            competition_list.append(competition_name)

        return competition_dict, competition_list
