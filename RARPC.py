import argparse
from colorama import Fore, Style, init
import configparser
from datetime import datetime
from pprint import pprint
from pypresence import Presence 
import re
import requests
import time
import os.path

init(autoreset=True)

def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(Fore.RED + f"Failed to fetch data from {url}, status code: {response.status_code}")
        return None

def sanitize_console_name(console_name):
    sanitized_name = re.sub('[^0-9a-zA-Z]+', '', console_name)
    return sanitized_name.lower()

def update_presence(RPC, data, game_data, start_time, username):
    release_date = datetime.strptime(game_data['Released'], '%B %d, %Y')
    year_of_release = release_date.year
    details = f"{game_data['GameTitle']} ({year_of_release})"
    RPC.update(
        state=data["RichPresenceMsg"],
        details=details,
        start=start_time,
        large_image="ra_logo",
        large_text=f"Released {game_data['Released']}, Developed by {game_data['Developer']}, Published by {game_data['Publisher']}",
        small_image=sanitize_console_name(game_data['ConsoleName']),
        small_text=game_data['ConsoleName'],
        buttons=[{"label": "View RA Profile", "url": f"https://retroachievements.org/user/{username}"}]
    )

def setup_config():
    config_file = open("config.ini","w")
    print(f'Enter RetroAchievements username: ')
    usr = input()
    print(f'Enter RetroAchievements api_key: ')
    api = input()  

    data = "[DISCORD]\nusername = "+str(usr)+"\napi_key = "+str(api)+"\nclient_id = -1"

    config_file.write(data)
    config_file.close()

def main():
    if(os.path.exists('config.ini') == False):
        print(Fore.YELLOW + f"Config file not found. Running first time setup...")
        setup_config()

    config = configparser.ConfigParser()
    config.read('config.ini')
    
    username = config.get('DISCORD', 'username')
    api_key = config.get('DISCORD', 'api_key')
    client_id = config.get('DISCORD', 'client_id') if config.has_option('DISCORD', 'client_id') else "1249693940299333642"
    if(client_id == "-1"):
        client_id = "1249693940299333642"

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Print debug information')
    parser.add_argument('--fetch', type=int, default=30, help='Time to sleep before fetches in seconds')
    args = parser.parse_args()

    profile_url = f"https://retroachievements.org/API/API_GetUserProfile.php?u={username}&y={api_key}&z={username}"

    start_time = int(time.time())

    RPC = Presence(client_id)
    print(Fore.CYAN + "Connecting to Discord App...")
    RPC.connect()
    print(Fore.MAGENTA + "Connected!")

    while True:
        print(Fore.CYAN + f"Fetching {username}'s RetroAchievements activity...")
        data = get_data(profile_url)
        if data is None:
            break

        print(Fore.MAGENTA + f"Result: {data['RichPresenceMsg']}")

        game_params = f"?z={username}&y={api_key}&i={data['LastGameID']}"
        game_url = f"https://retroachievements.org/API/API_GetGame.php{game_params}"
        print(Fore.CYAN + "Fetching game data...")
        game_data = get_data(game_url)
        if game_data is None:
            break

        print(Fore.MAGENTA + f"Result: {game_data['GameTitle']}")

        if args.debug:
            print(Fore.YELLOW + "Debug game data:")
            pprint(game_data)

        update_presence(RPC, data, game_data, start_time, username)

        print(Fore.CYAN + f"Sleeping for {args.fetch} seconds...")
        time.sleep(args.fetch)

if __name__ == "__main__":
    main()
