# Hockey Team Tracker for Home Assistant
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

## About
A simple custom component to track the upcoming match from a dutch field hockey teams using the HockeyWeerelt api.

## Usage
Add a team using the config flow at Settings > Devices & Services > Add integration > Hockey Team Tracker.
Select a club which has a team you want to track.
Select a team and optionally give a sensor name, if you want to select more teams from one club, click the checkmark.

### Manual
I dont recommend manually adding a sensor, but it is possible with the following scheme:

sensor:
  - platform: hockey_team_tracker
  club: N103 | optional
  club_name: Goudse MHC | optional
  teams: | required
  - team: N15163 | required
    team_name: D1 Zaal | optional
    name: Goudse MHC D1 | optional
  - team: N10814
    team_name: H1 Zaal
    name: Goudse MHC H1
  - team: N33801
    team_name: H2 Zaal
    name: Goudse MHC H2

## Output
The sensors it creates do an api call to https://publicaties.hockeyweerelt.nl/mc/teams/{team_id}/matches/upcoming?show_all=0 and sets the attributes to $.data[0] every 10 minutes.

Use a custom card to display the data for example.

![image](https://github.com/joosthoi1/hockey-team-tracker/assets/44155686/203eb594-04e1-4618-a5b3-a11d60b412ef)
