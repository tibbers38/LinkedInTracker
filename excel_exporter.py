from datetime import datetime
import sqlite3
from openpyxl.utils import get_column_letter

import pandas as pd
from openpyxl import Workbook, worksheet
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.styles import Border, Side
from openpyxl.styles import PatternFill
from openpyxl.formatting.rule import CellIsRule

class ExcelExporter:

    def __init__(self):
        self.conn = None
        self.data = None
        self.workbook = None
        self.games = []
        self.players = []

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
        self.games = sorted(self.data["Game"].unique())
        self.players = sorted(self.data["PlayerName"].unique())

        print(f"[+] Loaded {len(self.data)} records")

    def create_workbook(self):
        self.workbook = Workbook()

        default_sheet = self.workbook.active
        self.workbook.remove(default_sheet)

        print("[+] Workbook created")
    
    def create_game_sheet(self, game_name):
        worksheet = self.workbook.create_sheet(game_name)
        game_data = self.data[self.data["Game"] == game_name]
        game_data = game_data[
            ["ActualDate", "PlayerName", "LocalRank", "TimeElapsed", "HintFree", "MistakeFree"]
        ]
        game_data = game_data.sort_values(by=["ActualDate", "PlayerName"])
        worksheet.append(game_data.columns.tolist())
        for row in game_data.itertuples(index=False):
            worksheet.append(row)
        self.format_header(worksheet)
        self.auto_fit_columns(worksheet)
        self.add_borders(worksheet)
        self.freeze_header(worksheet)
        self.add_filter(worksheet)
        self.apply_conditional_formatting(worksheet)

    def create_summary_sheet(self):
        worksheet = self.workbook.create_sheet("Summary")

        worksheet["A1"] = "LinkedIn Games Tracker"
        worksheet["A3"] = "Report Generated"
        worksheet["B3"] = datetime.now()
        worksheet["A4"] = "Latest Game Data"
        last_update = self.data["ActualDate"].max()
        worksheet["B4"] = last_update
        worksheet["A6"] = "Total Days"
        total_days = self.data["ActualDate"].nunique()
        worksheet["B6"] = total_days
        worksheet["A7"] = "Players"
        total_players = len(self.data["PlayerName"].unique())
        worksheet["B7"] = total_players
        worksheet["A8"] = "Games"
        total_games = len(self.data["Game"].unique())
        worksheet["B8"] = total_games
        self.format_header(worksheet)
        self.auto_fit_columns(worksheet)
        self.write_overall_statistics(worksheet)
        self.write_latest_results(worksheet)
        self.write_performance_statistics(worksheet)

    def get_overall_statistics(self):
        statistics = (
            self.data
            .groupby("PlayerName")
            .agg(
                Games=("PlayerName", "count"),
                Wins=("LocalRank", lambda x: (x == 1).sum()),
                AvgRank=("LocalRank", "mean"),
                AvgTime=("TimeElapsed", "mean"),
            )
        )
        statistics["AvgRank"] = statistics["AvgRank"].round(2)
        statistics["AvgTime"] = statistics["AvgTime"].round(1)
        return statistics
    
    def write_overall_statistics(self, worksheet):
        statistics = self.get_overall_statistics()
        worksheet.append([])
        worksheet.append(["Overall Statistics"])
        worksheet.append(statistics.reset_index().columns.tolist())
        for row in statistics.reset_index().itertuples(index=False):
            worksheet.append(row)

    def get_latest_results(self):
        # Lấy ngày mới nhất của từng game
        latest_dates = (
            self.data
            .groupby("Game")
            .agg(
                ActualDate=("ActualDate", "max")
            )
            .reset_index()
        )
        # Join lại với bảng gốc để lấy toàn bộ dữ liệu của ngày đó
        latest_results = latest_dates.merge(
            self.data,
            on=["Game", "ActualDate"]
        )
        # Chỉ lấy những cột cần thiết
        latest_results = latest_results[
            [
                "Game",
                "PlayerName",
                "LocalRank"
            ]
        ]
        # Pivot thành bảng
        latest_results = latest_results.pivot(
            index="PlayerName",
            columns="Game",
            values="LocalRank"
        )
        return latest_results

    def write_latest_results(self, worksheet):
        latest_results = self.get_latest_results()
        worksheet.append([])
        worksheet.append(["Latest Results"])
        worksheet.append(latest_results.reset_index().columns.tolist())
        for row in latest_results.reset_index().itertuples(index=False):
            worksheet.append(row)

    def get_performance_statistics(self):
        performance_stats = (
            self.data
            .groupby("PlayerName")
            .agg(
                WinRate=("LocalRank", lambda x: (x == 1).mean()),
                HintFreeRate=("HintFree", "mean"),
                MistakeFreeRate=("MistakeFree", "mean"),
            )
        )
        perfect_rate = (
            self.data
            .groupby("PlayerName")
            .apply(
                lambda group: (
                    (group["HintFree"] == 1)
                    &
                    (group["MistakeFree"] == 1)
                ).mean(),
                include_groups=False
            )
        )
        performance_stats["PerfectRate"] = perfect_rate
        return performance_stats

    def write_performance_statistics(self, worksheet):
        performance_stats = self.get_performance_statistics()
        worksheet.append([])
        worksheet.append(["Performance Statistics"])
        header_row = worksheet.max_row + 1
        worksheet.append(
            performance_stats.reset_index().columns.tolist()
        )
        for row in performance_stats.reset_index().itertuples(index=False):
            worksheet.append(row)
        self.format_percentage_columns(
            worksheet,
            header_row,
            [
                "WinRate",
                "HintFreeRate",
                "MistakeFreeRate",
                "PerfectRate"
            ]
        )

    def get_column_letter_by_header(self, worksheet, header_row, header_name):
        for cell in worksheet[header_row]:
            if cell.value == header_name:
                return get_column_letter(cell.column)
        return None

    def format_percentage_columns(self, worksheet, header_row, headers):
        for header in headers:
            column = self.get_column_letter_by_header(
                worksheet,
                header_row,
                header
            )
            if column is None:
                continue
            for row in range(header_row + 1, worksheet.max_row + 1):
                worksheet[f"{column}{row}"].number_format = "0%"

    # These function are for formatting the Excel sheet, such as setting header styles, auto-fitting columns, adding borders, freezing the header row, adding filters, and applying conditional formatting.

    def format_header(self, worksheet):
        header_font = Font(
            bold=True,
            color="FFFFFF"
        )
        header_fill = PatternFill(
            fill_type="solid",
            fgColor="4472C4"
        )
        header_alignment = Alignment(
            horizontal="center",
            vertical="center"
        )
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment

    def auto_fit_columns(self, worksheet):
        for column in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                if cell.value is not None:
                    max_length = max(
                        max_length,
                        len(str(cell.value))
                    )
            worksheet.column_dimensions[column_letter].width = max_length + 3
    
    def add_borders(self, worksheet):
        thin = Side(
            style="thin",
            color="DDDDDD"
        )
        border = Border(
            left=thin,
            right=thin,
            top=thin,
            bottom=thin
        )
        for row in worksheet.iter_rows():
            for cell in row:
                cell.border = border

    def freeze_header(self, worksheet):
        worksheet.freeze_panes = "A2"
    
    def add_filter(self, worksheet):
        worksheet.auto_filter.ref = worksheet.dimensions

    def apply_conditional_formatting(self, worksheet):
        gold = PatternFill(
            fill_type="solid",
            fgColor="FFD700"
        )
        silver = PatternFill(
            fill_type="solid",
            fgColor="D9D9D9"
        )
        bronze = PatternFill(
            fill_type="solid",
            fgColor="F4B183"
        )
        worksheet.conditional_formatting.add(
            "C2:C1000",
            CellIsRule(
                operator="equal",
                formula=["1"],
                fill=gold
            )
        )
        worksheet.conditional_formatting.add(
            "C2:C1000",
            CellIsRule(
                operator="equal",
                formula=["2"],
                fill=silver
            )
        )
        worksheet.conditional_formatting.add(
            "C2:C1000",
            CellIsRule(
                operator="equal",
                formula=["3"],
                fill=bronze
            )
        )

    def save_workbook(self):
        self.workbook.save("result.xlsx")
        print("[+] Excel exported")

    def run(self):
        self.init_database()
        self.load_data()
        self.create_workbook()
        self.create_summary_sheet()
        for game in self.games:
            self.create_game_sheet(game)
        self.save_workbook()


if __name__ == "__main__":
    exporter = ExcelExporter()
    exporter.run()