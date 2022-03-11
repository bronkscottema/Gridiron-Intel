import requests


OpponentNFLList = []
WeekList = []
GameData = []
playIdNumber = []
def getNFLOpponent(yearOf, teamName):
    OpponentNFLList.clear()
    teamResponse = requests.get("https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams")
    for team in teamResponse.json()["sports"][0]["leagues"][0]["teams"]:
        if teamName == team["team"]["displayName"]:
            TeamId = team["team"]["id"]
            response = requests.get("https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/" + TeamId + "/schedule?" + yearOf)
            for opponentList in response.json()["events"]:
                if teamName == opponentList["competitions"][0]["competitors"][0]["team"]["displayName"]:
                    OpponentNFLList.append(opponentList["competitions"][0]["competitors"][1]["team"]["displayName"])
                else:
                    OpponentNFLList.append(opponentList["competitions"][0]["competitors"][0]["team"]["displayName"])
            return OpponentNFLList

def getNFLWeek(yearOf, teamName, opponent):
    teamResponse = requests.get("https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams")
    for team in teamResponse.json()["sports"][0]["leagues"][0]["teams"]:
        if teamName == team["team"]["displayName"]:
            TeamId = team["team"]["id"]
            response = requests.get(
                "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/" + TeamId + "/schedule?" + yearOf)
            for weekList in response.json()["events"]:
                if opponent == weekList["competitions"][0]["competitors"][0]["team"]["displayName"] and teamName == weekList["competitions"][0]["competitors"][1]["team"]["displayName"]:
                    WeekList.append(weekList['week']['text'])
                    return WeekList
                elif opponent == weekList["competitions"][0]["competitors"][1]["team"]["displayName"] and teamName == weekList["competitions"][0]["competitors"][0]["team"]["displayName"]:
                    WeekList.append(weekList['week']['text'])
                    return WeekList
                else:
                    continue

def getNFLGameData(teamName, yearOf, opponent):
    teamResponse = requests.get("https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams")
    for team in teamResponse.json()["sports"][0]["leagues"][0]["teams"]:
        if teamName == team["team"]["displayName"]:
            TeamId = team["team"]["id"]
            response = requests.get(
                "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/" + TeamId + "/schedule?" + yearOf)
            for weekList in response.json()["events"]:
                if opponent == weekList["competitions"][0]["competitors"][0]["team"]["displayName"] and teamName == weekList["competitions"][0]["competitors"][1]["team"]["displayName"]:
                    gameIdresponse = requests.get("http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/" + weekList['id'] + "/competitions/" + weekList['id'] + "/plays?limit=300")
                    for gameInfo in gameIdresponse.json()["items"]:
                        playIdNumber.append(weekList['id'])
                        GameData.append(gameInfo)

                    return GameData
                elif opponent == weekList["competitions"][0]["competitors"][1]["team"]["displayName"] and teamName == weekList["competitions"][0]["competitors"][0]["team"]["displayName"]:
                    gameIdresponse = requests.get(
                        "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/" + weekList[
                            'id'] + "/competitions/" + weekList['id'] + "/plays?limit=300")
                    for gameInfo in gameIdresponse.json()["items"]:
                        playIdNumber.append(weekList['id'])
                        GameData.append(gameInfo)

                    return GameData

                else:
                    continue