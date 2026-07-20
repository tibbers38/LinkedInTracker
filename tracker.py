import json
import sys
from pathlib import Path
from urllib import response
import requests
from dotenv import load_dotenv
import os
import sqlite3
from datetime import date, datetime

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

    def parse_response(self, game_name, data):
        players = []
        # Lấy leaderboard
        elements = data["data"]["data"][
            "identityDashGameConnectionsEntitiesByOptedInToLeaderboardAndPlayed"
        ]["elements"]
        # Tạo dictionary để map profile URN -> thông tin người dùng
        profiles = {}
        for profile in data.get("included", []):
            urn = profile.get("entityUrn")
            if urn:
                profiles[urn] = {
                    "first_name": profile.get("firstName", ""),
                    "last_name": profile.get("lastName", "")
                }
        # Parse leaderboard
        for element in elements:
            profile_urn = element["playerDetails"]["player"]["*profile"]
            profile = profiles.get(profile_urn, {})
            players.append({
                "game": game_name,
                "player_urn": profile_urn,
                "player_name": f'{profile.get("first_name", "")} {profile.get("last_name", "")}'.strip(),
                "rank": element.get("ranking"),
                "time_elapsed": element.get("gameScore", {}).get("timeElapsed"),
                "hint_free": element.get("completionAttributes", {}).get("isHintFree"),
                "mistake_free": element.get("completionAttributes", {}).get("isMistakeFree")
            })
        return players
    
    def save_players(self, players, retrieved_at):
        for player in players:
            self.cursor.execute("""
                INSERT INTO Leaderboard (
                    RetrievedAt,
                    Game,
                    PlayerUrn,
                    PlayerName,
                    Rank,
                    TimeElapsed,
                    HintFree,
                    MistakeFree
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                retrieved_at.isoformat(),
                player["game"],
                player["player_urn"],
                player["player_name"],
                player["rank"],
                player["time_elapsed"],
                player["hint_free"],
                player["mistake_free"]
            ))
        self.conn.commit()
        print(f"[+] Saved {len(players)} players")

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

    from datetime import date

    def has_today_snapshot(self):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM Leaderboard
            WHERE date(RetrievedAt) = ?
        """, (date.today().isoformat(),))
        count = self.cursor.fetchone()[0]
        return count > 0
    
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
        if self.has_today_snapshot():
            print("[+] Today's snapshot already exists.")
            return
        # self.print_games()
        for game_name, game_urn in self.config["games"].items():
            response = self.fetch_game(game_name, game_urn)
            data = response.json()
            if not response.ok:
                print(response.status_code)
                print(response.text)
                continue
            data = response.json()
            players = self.parse_response(game_name, data)
            retrieved_at = datetime.now()
            self.save_players(players, retrieved_at)

if __name__ == "__main__":
    try:
        tracker = LinkedInTracker()
        tracker.run()

    except Exception as ex:
        print(f"[ERROR] {ex}")
        sys.exit(1)