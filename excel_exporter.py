import sqlite3

import pandas as pd
from openpyxl import Workbook


class ExcelExporter:

    def __init__(self):
        self.conn = None
        self.data = None
        self.workbook = None

    def init_database(self):
        self.conn = sqlite3.connect("leaderboard.db")
        print("[+] Database connected")

    def load_data(self):
        self.data = pd.read_sql_query(
            """
            SELECT *
            FROM Leaderboard
            ORDER BY ActualDate, Game, Rank
            """,
            self.conn
        )

        print(f"[+] Loaded {len(self.data)} records")

    def create_workbook(self):
        self.workbook = Workbook()

        default_sheet = self.workbook.active
        self.workbook.remove(default_sheet)

        print("[+] Workbook created")

    def create_summary_sheet(self):
        worksheet = self.workbook.create_sheet("Summary")

        worksheet["A1"] = "LinkedIn Games Tracker"
        worksheet["A3"] = "Total Records"
        worksheet["B3"] = len(self.data)

        print("[+] Summary sheet created")

    def save_workbook(self):
        self.workbook.save("result.xlsx")
        print("[+] Excel exported")

    def run(self):
        self.init_database()
        self.load_data()
        self.create_workbook()
        self.create_summary_sheet()
        self.save_workbook()


if __name__ == "__main__":
    exporter = ExcelExporter()
    exporter.run()