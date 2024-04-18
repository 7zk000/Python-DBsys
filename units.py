import os
import sys
import firebase_admin
from firebase_admin import credentials
from config import config_load  # config_loadを直接インポート
import logging
from datetime import datetime

def initialize_firebase():
    """Firebase Admin SDKを初期化する"""
    config = config_load()
    FIREBASE_SDK_PATH = config["FIREBASE_SDK_PATH"]
    if not firebase_admin._apps:
        if not os.path.exists(FIREBASE_SDK_PATH):
            print("Firebaseサービスアカウントキーファイルが見つかりません。")
            sys.exit(1)
        cred = credentials.Certificate(FIREBASE_SDK_PATH)
        firebase_admin.initialize_app(cred)



def setup_logging():
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"(lo){current_datetime}.txt"
    log_directory = "debuglog"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_path = os.path.join(log_directory, log_filename)
    logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
