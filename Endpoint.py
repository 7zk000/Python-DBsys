import os
import sys
import subprocess
import requests
import json
import argparse
from config import config_load
from networkspeed import display_network_speed
from firebase_admin import firestore
from units import initialize_firebase,setup_logging


# 定数の定義
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.json')

# 設定の読み込み
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

GOOGLE_BOOKS_API_KEY = config["GOOGLE_BOOKS_API_KEY"]
FIREBASE_SDK_PATH = config["FIREBASE_SDK_PATH"]

def display_title():
    """プログラムのタイトルを表示する"""
    print("------はろー　わーるど!------")

def search_books(api_key, query="python"):
    """Google Books APIを使用して書籍情報を検索し、結果を表示する"""
    print(f"Google Booksから'{query}'に関連する書籍情報を検索します。")
    endpoint = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "key": api_key}
    try:
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            for book in data['items']:
                title = book['volumeInfo']['title']
                authors = book['volumeInfo'].get('authors', ['著者不明'])
                print(f"タイトル: {title}, 著者: {', '.join(authors)}")
        else:
            print(f"書籍情報の取得に失敗しました。ステータスコード: {response.status_code}")

    except requests.RequestException as e:
        print(f"書籍情報の取得中にエラーが発生しました: {e}")


def update_db():
    """データベースを更新するためのスクリプトを実行する"""
    script_path = os.path.join(BASE_DIR, 'midpoint.py')
    try:
        subprocess.run(['python', script_path, '--action', 'update'], check=True)
        print("DB更新機能の実行に成功しました。")
    except subprocess.CalledProcessError as e:
        print(f"DB更新機能の実行中にエラーが発生しました: {e}")

    except FileNotFoundError:
        print("midpoint.pyが見つかりません。ファイル名とパスを確認してください。")

    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")


def display_books_by_rating():
    """データベースに保存されている書籍の中から、評価順に書籍情報を表示する"""
    db = firestore.client()
    try:
        books_ref = db.collection('books').order_by('averageRating', direction=firestore.Query.DESCENDING)
        docs = books_ref.stream()
        for doc in docs:
            book = doc.to_dict()
            isbn = book.get('isbn', 'ISBN情報不明')
            print(f"タイトル: {book.get('title', 'タイトル不明')}, 平均評価: {book.get('averageRating', '評価不明')}, 著者: {', '.join(book.get('authors', ['著者不明']))}, ISBN: {isbn}")
    except Exception as e:
        print(f"書籍情報の取得に失敗しました: {e}")


def search_books_interactive(api_key):
    """インタラクティブモードで書籍検索、DB更新、評価順表示を行う"""
    display_title()
    while True:
        choice = input("1.検索, 2.DB更新, 3.最新の評価順を表示, 4.ネットワークの速度計測 ,終了するには'5'を入力してください: ")
        if choice == '1':
            query = input("検索したいキーワードを入力してください: ")
            search_books(api_key, query)
        elif choice == '2':
            update_db()
        elif choice == '3':
            display_books_by_rating()
        elif choice == '4':
            display_network_speed()
        elif choice == '5':
            print("------こんぷりーと!------")
            sys.exit(0)
        else:
            print("不正な入力だお！")


def main():
    """メイン関数"""
    config = config_load()
    GOOGLE_BOOKS_API_KEY = config["GOOGLE_BOOKS_API_KEY"]

    initialize_firebase()

    search_books_interactive(GOOGLE_BOOKS_API_KEY)

    parser = argparse.ArgumentParser(description='Endpoint.py')
    parser.add_argument('--api_key', help='Google Books APIキー', required=True)
    args = parser.parse_args()

    search_books_interactive(args.api_key)

if __name__ == '__main__':
    main()
