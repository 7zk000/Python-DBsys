import os
import subprocess
import sys
from config import config_load
from units import initialize_firebase, setup_logging
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.json')

def run_midpoint_script(update_decision):
    """midpoint.pyスクリプトを実行する"""
    script_path = os.path.join(BASE_DIR, 'Midpoint.py')
    if update_decision == '1':
        action = '--action update'
    else:
        print("DBの更新をスキップします。")
        return

    try:
        subprocess.run(['python', script_path, action], check=True)
        print("midpoint.pyの実行に成功しました。")
    except subprocess.CalledProcessError as e:
        print(f"実行中にエラーが発生しました: {e}")
    except FileNotFoundError:
        print("midpoint.pyが見つかりません。ファイル名とパスを確認してください。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        sys.exit(1)

def run_endpoint_script():
    """endpoint.pyスクリプトを実行する"""
    script_path = os.path.join(BASE_DIR, 'endpoint.py')
    try:
        subprocess.run(['python', script_path], check=True)
        #print("endpoint.pyの実行に成功しました。")
    except subprocess.CalledProcessError as e:
        print(f"endpoint.pyの実行中にエラーが発生しました: {e}")
    except FileNotFoundError:
        print("endpoint.pyが見つかりません。ファイル名とパスを確認してください。")
    except Exception as e:
        print(f"endpoint.pyの実行中に予期せぬエラーが発生しました: {e}")
        sys.exit(1)

def main():
    config_load()
    setup_logging()
    logging.info("save log....")
    initialize_firebase()

    update_decision = input("DB更新する？\n1.する　2.しない\n")
    run_midpoint_script(update_decision)
    run_endpoint_script()

if __name__ == '__main__':
    main()
