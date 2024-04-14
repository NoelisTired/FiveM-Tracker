# FiveM Tracker by NoelP (灰分 Ash)

This project is a Python application that allows you to look up players in a game without requiring admin permissions. It uses an in-game ID plugin to scan player IDs, submits them to Google OCR with an exploited API key, or manually browses all players by analyzing the server's endpoints.

## Description

This application uses the Google Vision API to perform OCR on player IDs obtained from the game. The application fetches data from the game server's endpoints and updates it every 5 minutes. The configuration for the application is managed by a configuration manager which loads a JSON configuration file.

## Getting Started

### Prerequisites

* Python 3.6 or higher
* Google Vision API key
* The following Python libraries: `pyautogui`, `keyboard`, `requests`, `io`, `base64`, `threading`, `time`, `os`, `json`, `re`

### Installing

1. Clone the repository
2. Install the required Python libraries using pip:

**pip** **install** **pyautogui** **keyboard** **requests** **io** **base64** **threading** **time** **os** **json** **re**

3. Add your Steam API key to the [`config.json`](vscode-file://vscode-app/c:/Users/nmjjp/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html "h:\Development Projects (small)\config.json") file:

**{**

**    **"**SteamAPI**"**:** **"**your_steam_api_key**"**,

**    **"**OCR**"**:** **true**

**}**

## Usage

Run the [`main.py`](vscode-file://vscode-app/c:/Users/nmjjp/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html "h:\Development Projects (small)\main.py") script to start the application:

**python** **main.py**

## Built With

* [Python](vscode-file://vscode-app/c:/Users/nmjjp/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html "https://www.python.org/") - The programming language used.
* [Google Vision API](vscode-file://vscode-app/c:/Users/nmjjp/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html "https://cloud.google.com/vision") - Used for OCR.

## Authors

* NoelP - *Initial work*

## Acknowledgments

* I should really rework this, thought just throw it out there; code is terrible
