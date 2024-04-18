import sys
import logging
import traceback
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import argparse
from config import config_load

class BooksManager:
    def __init__(self, api_key, db):
        self.api_key = api_key
        self.db = db

    def fetch_books(self):
        """Google Books APIから書籍情報を取得する"""
        print("書籍情報を取得中...")
        url = f"https://www.googleapis.com/books/v1/volumes?q=subject:fiction&orderBy=relevance&maxResults=40&key={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.HTTPError as e:
            logging.error(f"APIリクエストに失敗しました。ステータスコード: {e.response.status_code}, レスポンス: {e.response.text}")

            return None
        except requests.RequestException as e:
            logging.error(f"書籍情報の取得中にエラーが発生しました: {e}")
            traceback_str = ''.join(traceback.format_tb(e.__traceback__))
            logging.debug(f"スタックトレース: {traceback_str}")

            return None


    def extract_book_data(self, book):
        """書籍情報から必要なデータを抽出する"""
        return {
            'title': book['volumeInfo'].get('title', 'タイトル不明'),
            'authors': book['volumeInfo'].get('authors', ['著者不明']),
            'publisher': book['volumeInfo'].get('publisher', '出版社不明'),
            'publishedDate': book['volumeInfo'].get('publishedDate', '出版年不明'),
            'description': book['volumeInfo'].get('description', '概要不明'),
            'isbn_10': next((identifier['identifier'] for identifier in book['volumeInfo'].get('industryIdentifiers', []) if identifier['type'] == 'ISBN_10'), 'ISBN 10 不明'),
            'isbn_13': next((identifier['identifier'] for identifier in book['volumeInfo'].get('industryIdentifiers', []) if identifier['type'] == 'ISBN_13'), 'ISBN 13 不明'),
            'categories': book['volumeInfo'].get('categories', ['カテゴリー不明']),
            'averageRating': book['volumeInfo'].get('averageRating', 0),
            'ratingsCount': book['volumeInfo'].get('ratingsCount', 0),
            'language': book['volumeInfo'].get('language', '言語不明'),
        }

    def save_books_to_db(self, books):
        """取得した書籍情報をFirebaseのデータベースに保存する"""
        print("DBの保存中...", end="")
        total_books = len(books)
        for i, book in enumerate(books):
            book_data = self.extract_book_data(book)
            self.db.collection('books').add(book_data)
            percent_complete = ((i + 1) / total_books) * 100
            print(f"\rDBの保存中... {percent_complete:.2f}% 完了", end="")
        print("\n書籍情報の更新が完了しました。")

    def list_books(self):
        """データベースに保存されている書籍情報をリストアップする"""
        print("書籍情報のリストアップ中...")
        books_ref = self.db.collection('books').order_by('averageRating', direction=firestore.Query.DESCENDING)
        docs = books_ref.stream()
        for doc in docs:
            book = doc.to_dict()
            print(f"タイトル: {book.get('title', 'タイトル不明')}, 平均評価: {book.get('averageRating', '評価不明')}")

def main():
    config = config_load()
    GOOGLE_BOOKS_API_KEY = config["GOOGLE_BOOKS_API_KEY"]
    FIREBASE_SDK_PATH = config["FIREBASE_SDK_PATH"]

    # Firebaseの初期化
    cred = credentials.Certificate(FIREBASE_SDK_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    books_manager = BooksManager(GOOGLE_BOOKS_API_KEY, db)

    parser = argparse.ArgumentParser(description='DB更新と書籍情報の取得')
    parser.add_argument('--action', choices=['update', 'list'], help='実行するアクションを選択してください。')
    args = parser.parse_args()

    if args.action == 'update':
        books = books_manager.fetch_books()
        if books:
            books_manager.save_books_to_db(books)
            print("書籍情報の更新が完了しました。")
        else:
            print("書籍情報の取得に失敗しました。")
            sys.exit("Google Books APIの情報を確認してください。")
    elif args.action == 'list':
        books_manager.list_books()
    else:
        print("不正なアクションが指定されました。")


if __name__ == '__main__':
    main()
