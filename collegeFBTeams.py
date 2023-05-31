from __future__ import print_function
import cfbd
from cfbd.rest import ApiException
from dotenv import load_dotenv
import os

load_dotenv()


# Configure API key authorization: ApiKeyAuth
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = "838QllZxsFULyCZf4BRHZvwyMx9NEE12MQ1LE3T3NIePzC9WnunsOx71Zc5zhXB8"
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = cfbd.TeamsApi(cfbd.ApiClient(configuration))
api_game_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
TeamsList = []
OpponentList = []
CollegeWeekList = []

def getTeam():
    TeamsList.clear()
    try:
        # Play stats by play
        api_response = api_instance.get_fbs_teams()
        # pprint(api_response)
        for a in api_response:
            TeamsList.append(a.__getattribute__("school"))
        return TeamsList
    except ApiException as e:
        print("Exception when calling PlaysApi->get_play_stats: %s\n" % e)

def getOpponent(yearOf, regOrPost, teamName):
    OpponentList.clear()
    try:
        api_response = api_game_instance.get_games(year=int(yearOf), season_type= str(regOrPost), team=str(teamName))
        for a in api_response:
            if a.__getattribute__("away_team").lower() == teamName.lower():
                OpponentList.append(a.__getattribute__("home_team"))
            else:
                OpponentList.append(a.__getattribute__("away_team"))
        return OpponentList
    except ApiException as e:
        print("Exception when calling PlaysApi->get_play_stats: %s\n" % e)

def getWeek(yearOf, regOrPost, teamName, opponent):
    CollegeWeekList.clear()
    try:
        api_response = api_game_instance.get_games(year=int(yearOf), season_type= str(regOrPost), team=str(teamName))
        for a in api_response:
            if a.__getattribute__("away_team").lower() == opponent.lower():
                CollegeWeekList.append(a.__getattribute__("week"))
            elif a.__getattribute__("home_team").lower() == opponent.lower():
                CollegeWeekList.append(a.__getattribute__("week"))
        return CollegeWeekList
    except ApiException as e:
        print("Exception when calling PlaysApi->get_play_stats: %s\n" % e)