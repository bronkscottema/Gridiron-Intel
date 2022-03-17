from __future__ import print_function
import cfbd
import requests
from cfbd.rest import ApiException
import sys, os
from dotenv import load_dotenv

load_dotenv()

# Configure API key authorization: ApiKeyAuth
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = os.getenv("API_KEY")
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = cfbd.TeamsApi(cfbd.ApiClient(configuration))

nfl_player = []
college_player = []
home_college_player = []
away_college_player = []


def identify_college_player(year, team, jerseyNo):
    college_player.clear()
    try:
        # Play stats by play
        api_response = api_instance.get_roster(year=year, team=team)
        # pprint(api_response)
        i = []
        for i in enumerate(api_response):
            for j in enumerate(i):
                a = i[1]
                if a.first_name.lower() == jerseyNo.lower():
                    college_player.append(a)
                    return college_player

                elif a.last_name.lower() == jerseyNo.lower():
                    college_player.append(a)
                    return college_player

                try:
                    if a.jersey == int(jerseyNo):
                        college_player.append(a)
                        return college_player

                except:
                    continue
    except ApiException as e:
        print("Exception when calling PlaysApi->get_play_stats: %s\n" % e)


def get_whole_ncaa_home_roster(team, year):
    home_college_player.clear()
    api_response = api_instance.get_roster(year=year, team=team)
    # pprint(api_response)
    i = []
    for i in enumerate(api_response):
        if i[1].__getattribute__("jersey") is None and i[1].__getattribute__("first_name") is None and i[1].__getattribute__("last_name") is None:
            continue
        elif i[1].__getattribute__("jersey") is None:
            continue
        else:
            home_college_player.append(i[1])

    home_college_player.sort(key=lambda y: y.__getattribute__("jersey"))
    return home_college_player


def get_whole_ncaa_away_roster(team, year):
    away_college_player.clear()
    api_response = api_instance.get_roster(year=year, team=team)
    # pprint(api_response)
    i = []
    for i in enumerate(api_response):
        if i[1].__getattribute__("jersey") is None and i[1].__getattribute__("first_name") is None and i[1].__getattribute__("last_name") is None:
            continue
        elif i[1].__getattribute__("jersey") is None:
            continue
        else:
            away_college_player.append(i[1])

    away_college_player.sort(key=lambda y: y.__getattribute__("jersey"))
    return away_college_player


def identify_nfl_player(team_name, name_or_number):
    nfl_player.clear()
    teamResponse = requests.get("https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams")
    for team in teamResponse.json()["sports"][0]["leagues"][0]["teams"]:
        if team_name == team["team"]["displayName"]:
            TeamId = team["team"]["id"]
            response = requests.get(
                "http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/" + TeamId + "/roster")
            for i in range(len(response.json()['athletes'][0]['items'])):
                first_name = response.json()['athletes'][0]['items'][i]['firstName']
                last_name = response.json()['athletes'][0]['items'][i]['lastName']
                jersey = response.json()['athletes'][0]['items'][i]['jersey']
                if name_or_number == first_name or name_or_number == last_name or name_or_number == jersey:
                    nfl_player.append(first_name)
                    nfl_player.append(last_name)
                    nfl_player.append(jersey)
                    return nfl_player
        else:
            TeamId = team["team"]["id"]
            response = requests.get(
                "http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/" + TeamId + "/roster")
            for i in range(len(response.json()['athletes'][1]['items'])):
                first_name = response.json()['athletes'][1]['items'][i]['firstName']
                last_name = response.json()['athletes'][1]['items'][i]['lastName']
                jersey = response.json()['athletes'][1]['items'][i]['jersey']
                if name_or_number == first_name or name_or_number == last_name or name_or_number == jersey:
                    nfl_player.append(first_name)
                    nfl_player.append(last_name)
                    nfl_player.append(jersey)
                    return nfl_player