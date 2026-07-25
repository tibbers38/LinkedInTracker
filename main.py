import json

from tracker import LinkedInTracker
from excel_exporter import ExcelExporter
from graph_client import GraphClient

def main():
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    # Step 1: Retrieve leaderboard from LinkedIn and save to SQLite
    tracker = LinkedInTracker()
    tracker.run()

    # Step 2: Export SQLite data to Excel
    exporter = ExcelExporter()
    exporter.run()

    # Step 3: Upload Excel file to OneDrive using Microsoft Graph API
    # graph = GraphClient(
    #     client_id=config["graph"]["client_id"],
    #     tenant_id=config["graph"]["tenant_id"],
    #     scopes=config["graph"]["scopes"],
    # )
    # graph.authenticate()
    # graph.upload_file(
    #     local_path="result.xlsx",
    #     remote_path="Documents/result.xlsx",
    # )

if __name__ == "__main__":
    main()