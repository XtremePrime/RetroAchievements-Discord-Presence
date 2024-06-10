import argparse
from colorama import Fore, Style, init
from pprint import pprint
from pypresence import Presence 
import requests
import time

init(autoreset=True)

def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(Fore.RED + f"Failed to fetch data from {url}, status code: {response.status_code}")
        return None

def update_presence(RPC, data, game_data, start_time):
    details = f"{game_data['GameTitle']} ({game_data['ConsoleName']})"
    RPC.update(
        state=data["RichPresenceMsg"],
        details=details,
        start=start_time,
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('api_key')
    parser.add_argument('rpc_client_id')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    profile_url = f"https://retroachievements.org/API/API_GetUserProfile.php?u={args.username}&y={args.api_key}&z={args.username}"

    start_time = int(time.time())

    RPC = Presence(args.rpc_client_id)
    print(Fore.CYAN + "Connecting to Discord App...")
    RPC.connect()
    print(Fore.MAGENTA + "Connected!")

    while True:
        print(Fore.CYAN + f"Fetching {args.username}'s RetroAchievements activity...")
        data = get_data(profile_url)
        if data is None:
            break

        print(Fore.MAGENTA + f"Result: {data['RichPresenceMsg']}")

        game_params = f"?z={args.username}&y={args.api_key}&i={data['LastGameID']}"
        game_url = f"https://retroachievements.org/API/API_GetGame.php{game_params}"
        print(Fore.CYAN + "Fetching game data...")
        game_data = get_data(game_url)
        if game_data is None:
            break

        print(Fore.MAGENTA + f"Result: {game_data['GameTitle']}")

        if args.debug:
            print(Fore.YELLOW + "Debug game data:")
            pprint(game_data)

        update_presence(RPC, data, game_data, start_time)

        print(Fore.CYAN + "Sleeping...")
        time.sleep(30)

if __name__ == "__main__":
    main()