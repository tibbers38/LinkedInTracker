from tracker import LinkedInTracker
from excel_exporter import ExcelExporter


def main():
    # Step 1: Retrieve leaderboard from LinkedIn and save to SQLite
    tracker = LinkedInTracker()
    tracker.run()

    # Step 2: Export SQLite data to Excel
    exporter = ExcelExporter()
    exporter.run()


if __name__ == "__main__":
    main()