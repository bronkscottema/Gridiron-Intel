from __future__ import print_function

import os
import cfbd
from cfbd.rest import ApiException
from dotenv import load_dotenv

load_dotenv()

# Configure API key authorization: ApiKeyAuth
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = "838QllZxsFULyCZf4BRHZvwyMx9NEE12MQ1LE3T3NIePzC9WnunsOx71Zc5zhXB8"
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_game_instance = cfbd.PlaysApi(cfbd.ApiClient(configuration))
PlayList = []
def getGameData(year, team, opponent, regOrPost, week):
    PlayList.clear()
    try:
        # This if statement only for if a team is playing Lafayette a bug in the API for sure
        if opponent == 'Lafayette':
            opponent = 'Navy'
            week = 2
            api_response = api_game_instance.get_plays(year=year, week=week, offense=team, defense=opponent,
                                                       season_type=regOrPost)
            for a in api_response:
                PlayList.append(a)
            return PlayList

        api_response = api_game_instance.get_plays(year=year, week=week, offense=team, defense=opponent, season_type=regOrPost)

        for a in api_response:
            PlayList.append(a)
        return PlayList
    except ApiException as e:
        print("Exception when calling PlaysApi->get_play_stats: %s\n" % e)