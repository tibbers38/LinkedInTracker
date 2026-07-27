#!/bin/bash

set -e

PROJECT_DIR="/home/homelab/Projects/LinkedInTracker"

cd "$PROJECT_DIR"

mkdir -p logs

echo "========== $(date) ==========" >> logs/tracker.log

"$PROJECT_DIR/.venv/bin/python" main.py >> logs/tracker.log 2>&1
