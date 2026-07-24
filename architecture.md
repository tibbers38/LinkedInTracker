# LinkedIn Games Tracker Architecture

## Overview

The project automatically retrieves LinkedIn Games leaderboard data, stores it in SQLite, generates an analytical Excel report, and (future) uploads the report to OneDrive via Microsoft Graph.

```
LinkedIn
      │
      ▼
tracker.py
      │
      ▼
leaderboard.db (SQLite)
      │
      ▼
excel_exporter.py
      │
      ▼
LinkedIn Games.xlsx
      │
      ▼
graph_client.py (Future)
      │
      ▼
OneDrive
```

---

# Project Structure

```
linkedin-games-tracker/

tracker.py
excel_exporter.py
graph_client.py          # Future
config.py                # Future
requirements.txt

leaderboard.db
LinkedIn Games.xlsx
```

---

# Components

## tracker.py

Responsible for:

- Downloading leaderboard data
- Parsing LinkedIn responses
- Updating SQLite
- Maintaining historical data

SQLite is the single source of truth.

---

## leaderboard.db

Stores all historical game results.

Main table contains:

- ActualDate
- Game
- PlayerName
- TimeElapsed
- HintFree
- MistakeFree
- LocalRank

Excel is always regenerated from this database.

---

## excel_exporter.py

Responsible for:

- Loading SQLite into pandas DataFrames
- Computing analytics
- Creating Excel workbook
- Formatting worksheets
- Saving final report

This module contains both analytics and rendering.

Typical workflow:

```
run()

↓

load_data()

↓

create_workbook()

↓

create_summary_sheet()

↓

create_game_sheet()

↓

save_workbook()
```

---

# Design Pattern

Analytics and Excel rendering are separated by method.

Example:

```
get_overall_statistics()

↓

DataFrame

↓

write_overall_statistics()
```

Same pattern applies to every dashboard block.

```
get_latest_results()
write_latest_results()

get_performance_statistics()
write_performance_statistics()

...
```

---

# Workbook Structure

```
Summary

Crossclimb

Queens

Zip

Pinpoint

Tango

Mini Sudoku

Patches
```

Each game sheet contains raw historical data.

Summary contains aggregated analytics.

---

# Summary Dashboard

Contains multiple independent sections.

## Report Information

- Report Generated
- Latest Game Data
- Players
- Games
- Total Days

---

## Overall Statistics

Per-player metrics:

- Games
- Wins
- Average Rank
- Average Time

---

## Latest Results

Latest available result for every game.

Pivot table format.

---

## Performance Statistics

Per-player metrics:

- Win Rate
- Hint-Free Rate
- Mistake-Free Rate
- Perfect Rate

---

# Formatting

Implemented with openpyxl.

Includes:

- Borders
- Header styling
- AutoFilter
- Freeze Panes
- Auto column width
- Conditional Formatting
- Percentage formatting

Percentage formatting is applied using each block's header row rather than assuming row 1.

---

# Future Component

graph_client.py

Responsibilities:

- Authenticate using MSAL
- Acquire access token
- Upload Excel report
- Download files (optional)

Workflow:

```
Excel

↓

MSAL Authentication

↓

Microsoft Graph

↓

OneDrive
```

Authentication will use:

- Device Code Flow
- Delegated Permissions
- Public Client
- No Client Secret

Required permissions:

- User.Read
- Files.ReadWrite
- offline_access

---

# Architecture Principles

- SQLite is the single source of truth.
- Excel is generated from scratch every run.
- Analytics are calculated from pandas DataFrames.
- Excel only presents data.
- Microsoft Graph is responsible only for file transport.