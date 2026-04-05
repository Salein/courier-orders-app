#!/usr/bin/env bash
# Start the FastAPI backend server

set -e

cd "$(dirname "$0")"

# Check if virtual env exists
if [ ! -d ".venv" ]; then
    echo "No .venv found. Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source .venv/bin/activate

echo "Starting Courier Orders API on http://0.0.0.0:8000"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
