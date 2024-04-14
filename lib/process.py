import re
import requests
import datetime
from lib.config_manager import ConfigManager
from lib.ocr import ScreenTextDetector
import json, time, threading, keyboard, os

class Data:
    """
        This class is responsible for fetching the data from the server. It is also responsible for updating the data every 5 minutes.
    """
    def __init__(self, ip, port):
        super().__init__()
        self.ip, self.port = ip, port
        self.config = ConfigManager()
        self.info = {}
        self.screenshot = ScreenTextDetector()
        if self.config.get_config('OCR'):
            keyboard.add_hotkey("ctrl+f10", self.useOCR)
        keyboard.add_hotkey(".", self.cls)
        keyboard.add_hotkey("\\", self.get_all_players)
        keyboard.add_hotkey("'", self.serverInfo)
        keyboard.add_hotkey("ctrl+=", self.lookup_player)
        threading.Thread(target=self.fetch).start()

    def cls(self):
        print("\033c")
        self.domenu()

    """
        Calls the OCR function to take a screenshot and use the OCR to fetch the data.
    """
    def useOCR(self):
        response = self.screenshot.take_screenshot()
        if isinstance(response, list):
            for player in response:
                print("Player [%s]" % (player))
                time.sleep(1)
                self.lookup_player(player, compact=True)
                time.sleep(2)
        else:
            print(response)

    def get_all_players(self):
        for player in self.info['players.json']:
            print(f"{player['name']} - {player['id']} | {player['ping']}ms")

    """
        This function is responsible for fetching the status of the player via steam API.
    """
    @staticmethod
    def get_status(state):
        return {
            "0": "Offline / Private",
            "1": "Online",
            "2": "Busy",
            "3": "Away",
            "4": "Snooze",
            "5": "Looking to Trade",
            "6": "Looking to Play"
        }.get(state)

    """
        This function is responsible for fetching the identifiers of the player.
    """
    def getIdentifiers(self, data):
        x = re.findall(r"(\w+):(\w+)", data)
        sample = {
            'Steam': 'N/A',
            'Steam Name': 'N/A',
            'Steam Avatar': 'N/A',
            'Steam Created At': 'N/A',
            'Status': 'N/A',
            'License': 'N/A',
            'Discord': 'N/A',
            'Discord Name': 'N/A',
            'Created At': 'N/A',
            'Avatar': 'N/A',
            'Fivem': 'N/A',
            'License2': 'N/A',
            "Live": "N/A"
        }
        sample.update({x[0].capitalize(): x[1] if x[1] != '' else 'N/A' for x in x})
        if sample['Discord']:
            try:
                x = requests.get(f"https://discordlookup.mesavirep.xyz/v1/user/{sample['Discord']}", timeout=10)
                if x.status_code == 200:
                    y = x.json()
                    sample.update({'Discord Name': y['username'], 'Created at': y['created_at'], 'Avatar': y['avatar']['link']})
            except requests.Timeout:
                print("Discord API Exceeded 10000ms")
        if self.config.get_config('SteamAPI') != "APIKEY HERE" and sample['Steam'] != "N/A":
            steam_hex = str(int(sample['Steam'], base=16))
            try:
                x = requests.get(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.config.get_config('SteamAPI')}&steamids={str(steam_hex)}")
                if x.status_code == 200 and x.text != '{"response":{"players":[]}}':
                    y = x.json()
                    sample.update({
                        'Steam Name': y['response']['players'][0]['personaname'],
                        'Status': self.get_status(str(y['response']['players'][0]['profilestate'])),
                        'Steam Avatar': y['response']['players'][0]['avatarfull'],
                        'Steam Created At': datetime.datetime.fromtimestamp(y['response']['players'][0]['timecreated']).strftime("%d-%m-%Y %H:%M:%S")
                    })
            except requests.Timeout:
                print("Steam API Exceeded 10000ms")
        else:
            steam_hex = "N/A"
        return sample

    """
        Full on DOX the poor lad, this function is responsible for looking up the player.
    """
    def lookup_player(self, playerid=None, compact=False):
        if compact:
            player_info = """-------------------------------
Name: {name} | ID: {id} | Ping: {ping}ms
-------------------------------
Discord: {discord_name} | ID: {discord_id}
Steam: {steam_name} | HEX: {steam_hex}
FiveM ID: {fivem_id}
Xbox Live: {xbox_live}
-------------------------------
"""
        else:
            player_info = """----------------------------------------------
Name: {name} | ID: {id} | Ping: {ping}ms
----------------------------------------------
Discord:
    Discord ID: {discord_id}
    Discord Name: {discord_name}
    Created At: {discord_created_at}
    Avatar URL: {discord_avatar}
Steam:
    Display Name: {steam_name}
    HEX: {steam_hex} | DEC: {steam_dec}
    Status: {steam_status}
    Created At: {steam_status_created_at}
    Avatar URL: {steam_avatar}
FiveM:
    FiveM ID: {fivem_id}
    License: {fivem_license}
    License2: {fivem_license2}
Xbox:
    Xbox Live: {xbox_live}
----------------------------------------------
"""

        if not playerid:
            playerid = lambda x: x.isdigit() and int(x) or None
            playerid = playerid(input("Enter player ID: "))
        for player in self.info['players.json']:
            if player['id'] == playerid:
                identifiers = self.getIdentifiers(str(player['identifiers']))
                if compact:
                    print(player_info.format(
                        name=player['name'], id=player['id'], ping=player['ping'],
                        discord_name=identifiers['Discord Name'], discord_id=identifiers['Discord'],
                        steam_name=identifiers['Steam Name'], steam_hex=identifiers['Steam'],
                        fivem_id=identifiers['Fivem'], xbox_live=identifiers['Live']))
                else:
                    print(player_info.format(
                        name=player['name'], id=player['id'], ping=player['ping'],
                        discord_id=identifiers['Discord'], discord_name=identifiers['Discord Name'], discord_created_at=identifiers['Created At'], discord_avatar=identifiers['Avatar'],
                        steam_name=identifiers['Steam Name'], steam_hex=identifiers['Steam'], steam_dec=identifiers['Steam'], steam_status=identifiers['Status'], steam_status_created_at=identifiers['Steam Created At'],
                        steam_avatar=identifiers['Steam Avatar'], fivem_id=identifiers['Fivem'], fivem_license=identifiers['License'], fivem_license2=identifiers['License2'], xbox_live=identifiers['Live']))
                return
        print("The player you provided is not found.")

    """
        Export resources to hastebin, it is impossible to make it aesthetic in the console.
    """

    def export(self, data):
        formatted_data = ""
        for i, resource in enumerate(data):
            formatted_data += resource
            if (i + 1) % 10 != 0 and i < len(data) - 1:
                formatted_data += ", "
            else:
                formatted_data += "\n"
        r = requests.post("https://hastebin.skyra.pw/documents", data=formatted_data, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
        return(f"https://hastebin.skyra.pw/{r['key']}")
    
    """
        User Experience is mind-blowing, this function is responsible for displaying the server information.
    """
    def serverInfo(self):
        server_info = """
----------------------------------------------
Server Name: {server_name} | Server Description: {server_description}
Server IP: {server_ip}     | Server Port: {server_port}
----------------------------------------------
Game: {game} | Locales: {locales} | Players: {players}/{max_players}
----------------------------------------------
Map: {mapname} | Version: {version} | Gametype: {gametype}
----------------------------------------------
Resources: {resources}
----------------------------------------------
        """
        server = self.info['info.json']
        dynamic = self.info['dynamic.json']
        resources = self.export(server['resources'])
        print(server_info.format(
            server_name=server['vars']['sv_projectName'], server_description=server['vars']['sv_projectDesc'],server_ip=self.ip, server_port=self.port,
            game=dynamic['hostname'], locales=server['vars']['locale'], players=dynamic['clients'], max_players=dynamic['sv_maxclients'],
            mapname=dynamic['mapname'], version=server['version'], gametype=dynamic['gametype'], resources=resources)
        )

    """
        My naming skills are bad, but the two functions below are responsible for displaying the menu and fetching the data.
    """
    def domenu(self):
            print("""\
▄▄▄       ██████   ██░ ██ 
▒████▄   ▒██    ▒ ▒▓██░ ██ 
▒██  ▀█▄ ░ ▓██▄   ░▒██▀▀██ 
░██▄▄▄▄██  ▒   ██▒ ░▓█ ░██ 
 ▓█   ▓██▒██████▒▒ ░▓█▒░██▓
 ▒▒   ▓▒█▒ ▒▓▒ ▒ ░  ▒ ░░▒░▒
  ░   ▒▒ ░ ░▒  ░ ░  ▒ ░▒░ ░
  ░   ▒  ░  ░  ░    ░  ░░ ░
      ░        ░    ░  ░  ░
A powerful FiveM scraper created by NoelP
[.] Back
[CTRL + SHIFT + Q] Exit
""")
            if self.config.get_config('OCR'):
                print("[CTRL + F10] OCR")
            options = {
                "\\": "Show all Players",
                "'": "Show Server Info",
                "ctrl + =": "Look up player [REQUIRES INPUT]"
            }

            for key, value in options.items():
                print(f"{key}] {value}")
            print("\n\n")
    def menu(self):
        self.domenu()
    

    
    def update_info(self, file_path):
        self.info[file_path] = requests.get(f"http://{self.ip}:{self.port}/{file_path}").json()

    """
        This function is called in a separate thread to fetch the data every 5 minutes.
    """
    def fetch(self):
        while True:
            self.update_info('info.json')
            self.update_info('players.json')
            self.update_info('dynamic.json')
            time.sleep(300)  # Wait for 5 minutes before fetching again
