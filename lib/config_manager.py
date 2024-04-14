# config_manager.py
import json

class ConfigManager:
    def __init__(self, config_path="./config.json"):
        with open(config_path) as config_file:
            self.config = json.load(config_file)

    def get_config(self, key):
        return self.config.get(key)
