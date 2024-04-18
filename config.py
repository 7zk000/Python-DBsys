import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.json')

def config_load():
    """FirebaseとGoogle Books APIの設定を読み込む"""
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    return config
