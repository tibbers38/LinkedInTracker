# LinkedIn Games Tracker

## Overview
LinkedIn Games Tracker là một hệ thống tự động thu thập kết quả các trò chơi trên LinkedIn, lưu trữ lịch sử, tạo báo cáo Excel và phân phối báo cáo tới OneDrive.
Mục tiêu của project là xây dựng một hệ thống chạy hoàn toàn tự động trên Raspberry Pi.

# System Architecture

```
                        LinkedIn
                           │
                           ▼
                    Data Collection
                     (tracker.py)
                           │
                           ▼
                     SQLite Database
                    (leaderboard.db)
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
      Excel Export                 Statistics
 (excel_exporter.py)          (statistics.py)
            │
            ▼
      Excel Workbook
            │
            ▼
      Graph API Client
      (graph_client.py)
            │
            ▼
        Microsoft OneDrive
```

---

# Design Principles

- SQLite là nguồn dữ liệu duy nhất (Single Source of Truth).
- Mỗi module chỉ đảm nhiệm một nhiệm vụ.
- Không module nào phụ thuộc trực tiếp vào LinkedIn ngoài tracker.py.
- Các module có thể được thay thế độc lập.

---

# Project Structure

```
linkedin-games-tracker/
│
├── tracker.py
├── excel_exporter.py
├── graph_client.py
├── statistics.py
│
├── config.json
├── .env
│
├── leaderboard.db
│
├── output/
│   └── LinkedIn Games Tracker.xlsx
│
├── logs/
│
└── ARCHITECTURE.md
```

---

# Module Responsibilities

## tracker.py

Responsibilities

- Authenticate với LinkedIn
- Gọi GraphQL API
- Parse response
- Tính LocalRank
- Lưu dữ liệu vào SQLite
- Không tạo Excel
- Không upload file

Input

- config.json
- .env

Output

- leaderboard.db

---

## excel_exporter.py

Responsibilities

- Đọc SQLite
- Sinh Workbook
- Format Excel
- Tạo Dashboard

Input

- leaderboard.db

Output

- output/LinkedIn Games Tracker.xlsx

---

## statistics.py

Responsibilities

- Tính toán thống kê

Ví dụ

- Win Count
- Average Time
- Best Time
- Streak
- Ranking

Input

- leaderboard.db

Output

- JSON hoặc DataFrame

---

## graph_client.py

Responsibilities

- Authenticate Microsoft Graph
- Upload file lên OneDrive
- Sau này có thể:
    - Teams
    - SharePoint
    - Outlook

Input

- Excel Workbook

Output

- File trên OneDrive

---

# Database

Database

```
leaderboard.db
```

Main Table

```
Leaderboard
```

Columns

- RetrievedAt
- PuzzleDate
- Game
- PlayerUrn
- PlayerName
- Rank
- LocalRank
- TimeElapsed
- HintFree
- MistakeFree

SQLite được xem là nguồn dữ liệu duy nhất của toàn bộ hệ thống.

---

# Configuration

## config.json

Lưu các cấu hình không nhạy cảm.

Ví dụ

- GraphQL URLs
- Danh sách người chơi
- Mapping game

---

## .env

Lưu thông tin nhạy cảm.

Ví dụ

```
COOKIE=...

TENANT_ID=...
CLIENT_ID=...
CLIENT_SECRET=...

TOKEN_CACHE=token_cache.bin
```

Không commit file này lên Git.

---

# Hardware

Current Target

- Raspberry Pi 4
- 32GB+ SD Card hoặc SSD
- Internet

Không yêu cầu GPU.

---

# Software

Operating System

- Raspberry Pi OS Lite

Runtime

- Python 3.12+

Main Libraries

- requests
- sqlite3
- openpyxl
- msal
- python-dotenv

---

# Execution Flow

```
Cron

↓

tracker.py

↓

leaderboard.db

↓

excel_exporter.py

↓

LinkedIn Games Tracker.xlsx

↓

graph_client.py

↓

OneDrive
```

---

# Logging

Toàn bộ chương trình ghi log vào

```
logs/
```

Ví dụ

```
2026-08-01.log
```

Các thông tin cần log

- Start Job
- API Request
- API Error
- Insert Records
- Export Excel
- Upload Success
- Upload Failed

---

# Future Roadmap

## Version 1.0

- SQLite
- Excel Export
- Raspberry Pi
- OneDrive Upload

---

## Version 1.1

- Dashboard đẹp hơn
- Chart
- Win Rate
- Average Time

---

## Version 1.2

- Teams Notification
- Email Report

---

## Version 2.0

- Web Dashboard
- REST API
- Docker
- Multi-user