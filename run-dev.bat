@echo off
start "Eagle Taxi Backend" cmd /k "cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
start "Eagle Taxi Admin" cmd /k "cd admin && npm run dev -- --host 0.0.0.0 --port 5173"
start "Eagle Taxi Frontend" cmd /k "cd frontend && npm run dev -- --host 0.0.0.0 --port 5174"
