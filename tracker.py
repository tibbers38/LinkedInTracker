import json
import sys
from pathlib import Path
from urllib import response
import requests
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

csrf = os.getenv("CSRF_TOKEN")
cookie = os.getenv("COOKIE")

class LinkedInTracker:

    def __init__(self):
        self.config = None
        self.session = None
        self.conn = None
        self.cursor = None

    def load_config(self):
        with open("config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
        print("[+] Config loaded")

    def print_games(self):
        print("\nGames:")
        for game_name, game_urn in self.config["games"].items():
            print(f"  {game_name}")
            print(f"    {game_urn}")

    def parse_response(self, data):
        print("\n===== JSON =====\n")
        print(json.dumps(data, indent=4))

    def create_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "csrf-token": csrf,
            "cookie": cookie,
            "accept": "application/vnd.linkedin.normalized+json+2.1",
            "Referer": "https://www.linkedin.com/games/",
            "x-restli-protocol-version": "2.0.0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0"
        })
        print("[+] Session created")
    
    def init_database(self):
        self.conn = sqlite3.connect("leaderboard.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Leaderboard (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                RetrievedAt TEXT NOT NULL,
                Game TEXT NOT NULL,
                PlayerUrn TEXT,
                PlayerName TEXT,
                Rank INTEGER,
                TimeElapsed INTEGER,
                HintFree INTEGER,
                MistakeFree INTEGER
            )
        """)
        self.conn.commit()
        print("[+] Database initialized")

    def fetch_game(self, game_name, url):
        print(f"Fetching {game_name}")
        response = self.session.get(
            url,
            timeout=30
        )
        return response
    
    def run(self):
        self.load_config()
        self.create_session()
        self.init_database()
        self.print_games()
        for game_name, game_urn in self.config["games"].items():
            response = self.fetch_game(game_name, game_urn)
            data = response.json()
            self.parse_response(data)
            if response.ok:
                print("Success")
            else:
                print(response.status_code)
                print(response.text)


if __name__ == "__main__":
    try:
        tracker = LinkedInTracker()
        tracker.run()

    except Exception as ex:
        print(f"[ERROR] {ex}")
        sys.exit(1)