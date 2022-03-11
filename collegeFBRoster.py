from __future__ import print_function
import cfbd
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
year = int(paths[6]) # int | Year filter (optional)
team = str(paths[4]) # str | Team filter (optional)
jerseyNo= sys.argv[1]


def identifyPlayer(jerseyNo):
    try:
        # Play stats by play
        api_response = api_instance.get_roster(year=year, team=team)
        # pprint(api_response)
        i = []
        for i in enumerate(api_response):
            for j in enumerate(i):
                a = i[1]
                if a.first_name.lower() == jerseyNo.lower():
                    print(a.first_name)
                    print(a.last_name)
                    print(a.jersey)
                    return
                elif a.last_name.lower() == jerseyNo.lower():
                    print(a.first_name)
                    print(a.last_name)
                    print(a.jersey)
                    return
                try:
                    if a.jersey == int(jerseyNo):
                        print(a.first_name)
                        print(a.last_name)
                        print(a.jersey)
                        return
                except:
                    continue
    except ApiException as e:
        print("Exception when calling PlaysApi->get_play_stats: %s\n" % e)

identifyPlayer(jerseyNo)