# LinkedIn Games Tracker Architecture

## Overview

LinkedIn Games Tracker is an automated data collection and reporting pipeline that records daily LinkedIn Games leaderboard results and generates an interactive Excel dashboard.

The project consists of four logical layers:

1. Data Collection
2. Data Storage
3. Data Export
4. Business Intelligence (Excel Dashboard)

---

# Architecture

                    LinkedIn Games
                          │
                          ▼
                    tracker.py
                          │
                          ▼
                     SQLite Database
                    (Source of Truth)
                          │
                          ▼
                  excel_exporter.py
                          │
                          ▼
                    result.xlsx
                          │
                          ▼
                  Microsoft Graph API
                          │
                          ▼
                  OneDrive / SharePoint
                          │
                          ▼
                Summary.xlsx (Power Query)
                          │
                          ▼
             PivotTables / PivotCharts / KPIs

---

# Components

## tracker.py

Responsibilities

- Authenticate to LinkedIn
- Download leaderboard data
- Parse API responses
- Normalize raw records
- Store records into SQLite

This module never performs reporting or analytics.

---

## SQLite Database

SQLite is the single source of truth.

Responsibilities

- Store every leaderboard record
- Preserve historical data
- Support data export
- Support future querying

No calculated statistics are stored inside the database.

---

## export_excel.py

Responsibilities

- Read leaderboard data from SQLite
- Export RawData.xlsx
- Upload RawData.xlsx to OneDrive

No business logic or analytics are performed here.

---

## RawData.xlsx

This workbook is a normalized dataset.

Columns

- RetrievedAt
- ActualDate
- Game
- PlayerName
- LocalRank
- TimeElapsed
- HintFree
- MistakeFree

This workbook should not contain charts, PivotTables or dashboards.

---

## Dashboard.xlsx

Dashboard.xlsx is the reporting workbook.

It imports RawData.xlsx using Power Query.

Responsibilities

- Power Query transformations
- Data normalization
- Calculated columns
- PivotTables
- PivotCharts
- KPI cards
- Trend analysis

Dashboard.xlsx contains no manually entered data.

---

# Power Query Layer

Power Query is responsible for all data transformation.

Examples

- Rename columns
- Convert data types
- Add calculated columns
- Normalize values

Example calculated columns

- Score
- IsWinner
- PerfectGame
- Month
- Week
- Year

---

# Reporting Layer

The reporting layer is built entirely using PivotTables.

Example KPIs

- Average Rank
- Average Score
- Average Time
- Win Count
- Win Rate
- Hint-Free Rate
- Mistake-Free Rate
- Perfect Game Rate

Example Charts

- Rank Trend
- Score Trend
- Average Rank by Game
- Win Distribution
- Performance by Player

---

# Data Refresh Flow

23:00 Daily

↓

tracker.py

↓

SQLite

↓

RawData.xlsx

↓

Upload to OneDrive

↓

Next morning

↓

Open Dashboard.xlsx

↓

Refresh All

↓

Dashboard updated

---

# Design Principles

## Single Source of Truth

SQLite is the authoritative data source.

---

## Separation of Responsibilities

tracker.py

- Collect data

SQLite

- Store data

export_excel.py

- Export data

Power Query

- Transform data

PivotTables

- Analyze data

Dashboard

- Present data

---

## Advantages

- Minimal Python reporting code
- Easy to add new KPIs
- Easy to create new charts
- No dashboard logic inside Python
- Excel performs analytics using native features
- Clear separation between ETL and reporting

---

# Future Enhancements

Possible future improvements

- Automatic Dashboard refresh
- Power Automate integration
- Email report
- Teams notification
- Player performance prediction
- Historical leaderboard archive
- Power BI integration