"""
excel_exporter.py

Export leaderboard data from SQLite to Excel.
"""

from pathlib import Path
import sqlite3

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter


class ExcelExporter:
    """Export leaderboard database to Excel workbook."""

    def __init__(
        self,
        db_path: str = "leaderboard.db",
        output_file: str = "LinkedIn Games.xlsx",
    ):
        self.db_path = Path(db_path)
        self.output_file = Path(output_file)

        self.conn = None
        self.df = None

        self.workbook = Workbook()

        self.games = []
        self.players = []

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def export(self):
        """Main entry point."""

        self._load_data()

        self._create_summary_sheet()

        for game in self.games:
            self._create_game_sheet(game)

        self._apply_formatting()

        self._save()

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _load_data(self):
        """Load leaderboard data from SQLite."""

        self.conn = sqlite3.connect(self.db_path)

        query = """
        SELECT
            PuzzleDate,
            Game,
            PlayerName,
            Rank
        FROM Leaderboard
        ORDER BY PuzzleDate, Game, Rank
        """

        self.df = pd.read_sql_query(query, self.conn)

        self.games = sorted(self.df["Game"].unique())
        self.players = sorted(self.df["PlayerName"].unique())

    def _create_summary_sheet(self):
        """Create summary worksheet."""

        ws = self.workbook.active
        ws.title = "Summary"

        ws.append(["Game", "Records", "From", "To"])

        for game in self.games:

            df_game = self.df[self.df["Game"] == game]

            ws.append(
                [
                    game,
                    len(df_game),
                    df_game["PuzzleDate"].min(),
                    df_game["PuzzleDate"].max(),
                ]
            )

    def _create_game_sheet(self, game: str):
        """Create worksheet for a single game."""

        ws = self.workbook.create_sheet(title=game)

        df_game = self.df[self.df["Game"] == game]

        pivot = (
            df_game
            .pivot(
                index="PuzzleDate",
                columns="PlayerName",
                values="Rank",
            )
            .sort_index()
        )

        ws.append(["Date"] + list(pivot.columns))

        for date, row in pivot.iterrows():

            values = [date]

            values.extend(row.tolist())

            ws.append(values)

    def _apply_formatting(self):
        """Apply basic formatting."""

        for ws in self.workbook.worksheets:

            # Bold header
            for cell in ws[1]:
                cell.font = Font(bold=True)

            # Freeze header
            ws.freeze_panes = "A2"

            # Auto width
            for column_cells in ws.columns:

                length = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in column_cells
                )

                ws.column_dimensions[
                    get_column_letter(column_cells[0].column)
                ].width = length + 2

    def _save(self):
        """Save workbook."""

        self.workbook.save(self.output_file)

        if self.conn:
            self.conn.close()