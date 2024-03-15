import aiohttp
import asyncio


class Api:
    base_url = "https://publicaties.hockeyweerelt.nl"
    headers = {"Accept": "application/json"}
    session = None

    def __init__(self, session=None) -> None:
        if session is None:
            self.session = aiohttp.ClientSession()
        else:
            self.session = session

    async def fetch(self, url, params=None):
        async with self.session.get(
            url, params=params, headers=self.headers
        ) as response:
            return await response.json()

    async def get_clubs(self):
        return await self.fetch(f"{self.base_url}/mc/clubs")

    async def get_club_info(self, club):
        return await self.fetch(f"{self.base_url}/mc/clubs/{club}")

    async def get_club_teams(self, club):
        return await self.fetch(f"{self.base_url}/mc/clubs/{club}/teams")

    async def get_team_info(self, team):
        return await self.fetch(f"{self.base_url}/mc/teams/{team}")

    async def get_next_team_match(self, team, competition=None):
        params = {"show_all": 0}
        if competition:
            params["competition_id"] = competition
        matches = await self.fetch(
            f"{self.base_url}/mc/teams/{team}/matches/upcoming", params=params
        )
        return matches

    async def get_team_matches(self, team, competition):
        page = 0
        target = 1
        params = {"competition_id": competition, "show_all": 1}
        all_matches = []

        while page < target + 1:
            params["page"] = page
            page += 1

            requestData = await self.fetch(
                f"{self.base_url}/mc/teams/{team}/matches/upcoming",
                params=params,
            )
            all_matches += requestData["data"]
            target = requestData["meta"]["last_page"]

        return all_matches
