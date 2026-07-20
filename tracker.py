import json
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv
import os

load_dotenv()

csrf = os.getenv("CSRF_TOKEN")
cookie = os.getenv("COOKIE")

class LinkedInTracker:

    def __init__(self):
        self.config = None

    def load_config(self):
        with open("config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
        print("[+] Config loaded")

    def print_games(self):
        print("\nGames:")
        for game_name, game_urn in self.config["games"].items():
            print(f"  {game_name}")
            print(f"    {game_urn}")

    def run(self):
        self.load_config()
        self.create_session()
        self.print_games()
        for game_name, game_urn in self.config["games"].items():
            response = self.fetch_game(game_name, game_urn)
            print(response.text[:500])
            if response.ok:
                print("Success")
            else:
                print(response.status_code)
                print(response.text)

    def create_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            "csrf-token": csrf,
            "cookie": cookie,
            "accept": "application/vnd.linkedin.normalized+json+2.1",
            "x-restli-protocol-version": "2.0.0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0"
        })
        print("[+] Session created")
    
    def fetch_game(self, game_name, game_urn):
        params = {
            "includeWebMetadata": "true",
            "variables": f"(gameUrn:{game_urn},delta:1,start:0,count:15)",
            "queryId": self.config["graphql"]["queryId"]
        }
        print(f"\nFetching {game_name}...")
        response = self.session.get(
            self.config["graphql"]["url"],
            params=params,
            timeout=30
        )
        print(response.request.url)
        print(response.request.headers)
        print(params)
        print(response.status_code)
        return response


if __name__ == "__main__":
    try:
        tracker = LinkedInTracker()
        tracker.run()

    except Exception as ex:
        print(f"[ERROR] {ex}")
        sys.exit(1)