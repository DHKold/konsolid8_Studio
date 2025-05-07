import json
import os


class Settings:
    def __init__(self, config_file="settings.json"):
        self.config_file = config_file
        self.settings = {}

    def load(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.settings = json.load(f)

    def save(self):
        with open(self.config_file, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
