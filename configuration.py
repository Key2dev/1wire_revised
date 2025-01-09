import json
import os

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "debug_mode": True,
            "db_path": "temperatury.db",
            "table_name": "temps",
            "update_interval": 1000,  # in milliseconds
            "graph_points": 60,
            "temperature_range": [0, 50],
            "export_filename": "test_dbdump.csv"
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                self.default_config.update(loaded_config)
        else:
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.default_config, f, indent=4)

    def get(self, key):
        return self.default_config.get(key)

    def set(self, key, value):
        self.default_config[key] = value
        self.save_config()