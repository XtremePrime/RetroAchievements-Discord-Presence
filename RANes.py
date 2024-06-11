# XtremePrime 2024
# -- You will need to setup a discord application for this in order to work. To do so, follow the instructions in the README.md
# -- Please note: This will not be 100% accurate as it only uses latest data from your retro achievements page

import io
import requests
import sys
import time
from pypresence import Presence 

# The first argument of your python call should be your Username, then your API_KEY, then your Discord Application Client ID
# Ex: 
# > python RANes.py AverageUser 0X0X0X0X0X0X0X0X 123456789
USERNAME=str(sys.argv[1])
API_KEY=str(sys.argv[2])
RPC_CLIENT_ID = str(sys.argv[3])

profile_url = "https://retroachievements.org/API/API_GetUserProfile.php?u={0}&y={1}&z={2}".format(USERNAME, API_KEY, USERNAME)
print(profile_url)

RPC = Presence(RPC_CLIENT_ID)
print(">Connecting to Discord App...")
RPC.connect()
print(">Connected")

status = True

while(status):
    print(">GET profile game activity...")
    response = requests.get(profile_url)
    if response.status_code == 200:
        data = response.json()
        print(">Result: {0}".format(data["RichPresenceMsg"]))

        game_params = "?z={0}&y={1}&i={2}".format(USERNAME, API_KEY, data["LastGameID"])
        game_url = "{0}?{1}".format("https://retroachievements.org/API/API_GetGame.php", game_params)
        print(">GET game data...")
        game_response = requests.get(game_url)

        if game_response.status_code == 200:
            game_data = game_response.json()
            print(">Result: {0}".format(game_data["GameTitle"]))

            # Print each key-value pair in the game_data dictionary
            for key, value in game_data.items():
                print(f"{key}: {value}")
        else:
            print("Failed to fetch profile data:", response.status_code)
            status = False
            break;

    RPC.update(
        state=data["RichPresenceMsg"],
        details=game_data["GameTitle"],
        )

    print(">Sleeping...")
    time.sleep(30)