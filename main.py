import psutil, requests, time, threading, re
class Main:
    def __init__(self) -> None:
        self.lastUpdated = "05-02-2023"
        print("FiveM Player Scraper by @NoelP#3105 (NoelisTired)")
        print("Last updated: %s" % self.lastUpdated)
        self.get = Func()
        self.thread = self.thread()
        self.pid = None
    def scrapeServer(self):
        while True:
            for proc in psutil.process_iter():
                if "GTAProcess.exe" in proc.name():
                    self.pid = proc.pid
                    return
            time.sleep(3)
    def thread(self) -> None:
        print("Waiting for FiveM..")
        self.scrapeServer()
        while not self.get.ip:
            for connection in psutil.net_connections():
                if connection.pid == self.pid and connection.status == "ESTABLISHED" and connection.raddr[1] not in [80, 443] and connection.raddr[0] not in ["127.0.0.1", "localhost"]:
                    self.get.ip = connection.raddr[0]
                    self.get.port = connection.raddr[1]
                    print("Found FiveM! IP: %s, Port: %s" % (self.get.ip, self.get.port))
                    break
            time.sleep(1)
    @staticmethod
    def clear() -> None:
        print("\033c", end="")
        
    def mainMenu(self) -> None:
        self.clear()
        print("1. Get server info")
        print("2. Get ALL players")
        print("3. Get player info")
        print("4. Exit")
        opt = input("Select an option: ")
        self.clear()
        if opt == "1":
            print("Server info:")
            print("Steam required:",self.get.steamRequired)
            print("Resources:",len(self.get.resources))
            print("Discord:",self.get.discord)
            print("Language:",self.get.lang)
            input("Press enter to continue..")
        elif opt == "2":
            print("Players: %s" % len(self.get.players))
            [print(f"[{player[0]+1}]","FiveM ID:",player[1]['id'],"|","Name:",player[1]['name']) for player in enumerate(self.get.players)]
            input("Press enter to continue..")
        elif opt == "3":
            print("Players: %s" % len(self.get.players))
            opt = input("Select a player by ID: ")
            if not opt.isdigit():
                print("Invalid option!")
                time.sleep(1)
                return self.mainMenu()
            elif int(opt) > len(self.get.players):
                print("Invalid option!")
                time.sleep(1)
                return self.mainMenu()
            player = self.get.players[int(opt)-1]
            print("FiveM ID:",player['id'],"|","Name:",player['name'])
            print("Identifiers:")
            x = re.findall(r"(\w+):(\w+)", str(player['identifiers']))
            [print(x[0].capitalize(), x[1]) for x in x]
            print("Ping:",player['ping'],"ms")
            input("Press enter to continue..")
        elif opt == "4":
            exit()
        else:
            print("Invalid option!")
        self.mainMenu()
    def start(self) -> None:
        print("Starting..")
        thread = threading.Thread(target=self.get.Players)
        thread.daemon = True
        thread.start()
        self.mainMenu()
        
class Func:
    def __init__(self) -> None:
        self.players = None
        self.ip = None
        self.port = None
        self.steamRequired = None
        self.resources = None
        self.discord = None
        self.lang = None
    def Players(self) -> None:
        self.getServerInfo()
        while True:
            r = requests.get(f"http://{self.ip}:{self.port}/players.json")
            if r.status_code == 200:
                self.players = sorted(r.json(), key=lambda x: x["id"])
            time.sleep(5)
    def getServerInfo(self) -> None:
        r = requests.get(f"http://{self.ip}:{self.port}/info.json")
        if r.status_code != 200:
            return "No connection could be made because the target machine actively refused it."
        self.steamRequired = r.json()["requestSteamTicket"]
        self.resources = r.json()["resources"]
        self.discord = r.json()['vars']["discord"] if r.json()['vars']["discord"] != "" else "No discord link provided."
        self.lang = r.json()['vars']["locale"]
if __name__ == "__main__":
    print("\033c", end="")
    Main().start()