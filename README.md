# Hockey Team Tracker for Home Assistant
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

## About
A simple custom component to track the upcoming match from a dutch field hockey teams using the HockeyWeerelt api.
## Installation
HACS → Integrations → 3 dots → Custom repositories → Put https://github.com/joosthoi1/hockey-team-tracker under ‘repository’ → Put Integration as category → Click add and it should show up so you can download it.

## Usage
Add a team using the config flow at Settings > Devices & Services > Add integration > Hockey Team Tracker.
Select a club which has a team you want to track.
Select a team and optionally give a sensor name, if you want to select more teams from one club, click the checkmark.

### Manual
I dont recommend manually adding a sensor, but it is possible with the following scheme:

```yaml
sensor:  
  - platform: hockey_team_tracker  
  teams: | required  
  - team: N15163 | required  
    name: Goudse MHC D1 | required  
    competition: N12 | optional  
  - team: N10814  
    name: Goudse MHC H1  
  - team: N33801  
    name: Goudse MHC H2  
```


## Output
The sensors it creates do an api call to https://publicaties.hockeyweerelt.nl/mc/teams/{team_id}/matches/upcoming?show_all=0 and sets the attributes to $.data[0] every 10 minutes.

Use a custom card to display the data for example. I personally developed this card for the job, but you can use whatever you want.  https://github.com/MadSnuif/hockeynl-card

![image](https://github.com/joosthoi1/hockey-team-tracker/assets/44155686/203eb594-04e1-4618-a5b3-a11d60b412ef)
