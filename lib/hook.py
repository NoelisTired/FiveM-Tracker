import json
import os
import re
from trace import Trace
import requests
import time
import psutil
import threading
import logging, sys, asyncio
class FiveM:
    """
        I sincerely apologize for this constreuct, I am not proud of it.
    """
    def __init__(self):
        super().__init__()
        self.pid = None
        self.api_key = self.load_config('SteamAPI')
        self.ocr = self.load_config('OCR')
        self.servers = []  # List to store the server information
        self.ip, self.port = None, None
        self.incompactable = []
        logging.basicConfig(filename='log.txt', level=logging.DEBUG)
        print("\n[灰分 Ash] - Started Listening..")

    def load_config(self, key):
        with open("./config.json") as file:
            config = json.load(file)
        return config[key]

    def choose_server(self):
        os.system('cls')
        print("\n[灰分 Ash] - Found Servers:")
        for i, server in enumerate(self.servers):
            print(f"{i+1}. {server['server_name']} ({server['ip']}:{server['port']})")
        choice = input("Choose a server number (or 'q' to quit) or : ")
        if choice == 'q':
            sys.exit(0)
        try:
            index = int(choice) - 1
            if 0 <= index < len(self.servers):
                selected_server = self.servers[index]
                print("Selected Server:\n")
                print(f"Server Name: {selected_server['server_name']}")
                print(f"IP: {selected_server['ip']}")
                print(f"Port: {selected_server['port']}\n")
                time.sleep(3)
                os.system('cls')
                return(selected_server['ip'], selected_server['port'])
            else:
                print("Invalid choice. Please try again.")
                time.sleep(1.75)
        except ValueError:
            print("Invalid choice. Please try again.")
            time.sleep(1.75)
    """
        This server is resonsible for fetching processes, then choosing the server that it should attach to.
    """
    def receive(self):
        os.system('cls')
        print("\n[灰分 Ash] - Waiting for FiveM...")
        while not self.pid:
            for proc in psutil.process_iter(['name']):
                if 'FiveM.exe' in proc.name():
                    self.pid = proc.pid
                    os.system('cls')
                    print("\n[灰分 Ash] - FiveM Process ID:", self.pid)
                    time.sleep(3)
            os.system('cls')
            print("\n[灰分 Ash] - Scanning Connections")
            while True:
                self.scan_connections()
                if len(self.servers) != 0:
                    result = self.choose_server()
                    if isinstance(result, tuple):
                        return result
                self.servers.clear()
                time.sleep(1.25)
    """
        This function scans the ip adresses of the found processes.
    """
    def scan_connections(self):
            time.sleep(1.25)
            for connection in psutil.net_connections(kind='inet'):
                if self.is_valid_connection(connection) and not self.ip and connection.raddr[0] not in self.incompactable:
                    logging.info(connection)
                    self.handle_connection(connection)
        

    """
        This function is responsible for checking if the connection is valid.
    """
    def is_valid_connection(self, connection):
        return (
            (connection.pid == self.pid or connection.pid == 0) and
            (connection.raddr[1] not in [80, 443, 40120]) and
            (connection.raddr[0] not in ["127.0.0.1", "localhost", "192.168.0.1"])
        )

    """
        This function is deciding whether the server is compatible or not by fetching the dynamic.json file.
    """
    def handle_connection(self, connection):
        try:
            if self.is_valid_ip(connection.raddr[0]) and connection.raddr[0]:
                response = self.fetch_dynamic_json(connection.raddr[0], connection.raddr[1])
                if response != None:
                    if response.status_code == 200 and response.json().get("clients") > 0:
                        server_info = {
                            "server_name": response.json().get("hostname"),
                            "ip": connection.raddr[0],
                            "port": connection.raddr[1]
                        }
                        if server_info not in self.servers:
                            self.servers.append(server_info)  # Append server info to the list
                    else:
                        print("\n[灰分 Ash] - Incompatible server %s:%s" % (connection.raddr[0], connection.raddr[1]))
                        self.incompactable.append(connection.raddr[0])
            else:
                print("\n[灰分 Ash] - Bad IP: %s" % (connection.raddr[0]))
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching dynamic.json from {connection.raddr[0]}: {e}")
        except Exception as e:
            print(f"An error occurred while handling connection from {connection.raddr[0]}: {e}")


    def fetch_dynamic_json(self, ip, port):
        url = f"http://{ip}:{port}/dynamic.json"
        try:
            response = requests.get(url, timeout=3)
            return response
        except requests.exceptions.RequestException as e:
            return None

    """
        This function is responsible for checking if the IP is valid follwing the IPV4 format.
    """

    @staticmethod
    def is_valid_ip(ip):
        pattern = re.compile(r'^(([01]?\d{1,2}|2[0-4]\d|25[0-5])\.){3}([01]?\d{1,2}|2[0-4]\d|25[0-5])$')
        return bool(pattern.match(ip))

    def start(self):
        return self.receive()
        

