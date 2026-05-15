#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

osascript -e "tell app \"Terminal\" to do script \"cd '$ROOT_DIR/backend' && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000\""
osascript -e "tell app \"Terminal\" to do script \"cd '$ROOT_DIR/frontend' && npm run dev -- --host 0.0.0.0 --port 5173\""
