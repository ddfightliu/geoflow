@echo off
title Geoflow Setup
echo === Geoflow Environment Setup ===
REM 1. Activate venv
call .venv\Scripts\activate.bat
if errorlevel 1 (
  echo .venv activate failed
  pause
  exit /b 1
)
echo .venv OK

REM 2. Python deps
echo Installing Python deps...
uv sync
if errorlevel 1 (
  echo uv sync failed, fallback pip install
  python -m pip install -r requirements.txt
)
echo Python deps OK

REM 3. Frontend deps
echo Installing frontend deps...
if not exist frontend\bun.lock (
  echo No bun.lock, skipping
) else (
  cd frontend
  bun install
  cd ..
  echo Frontend deps OK
)

REM 4. Start services in new windows
echo Starting Backend...
start "Geoflow Backend" cmd /k "call .venv\Scripts\activate.bat && python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

echo Starting Frontend...
start "Geoflow Frontend" cmd /k "cd frontend && bun run dev"

echo Setup complete!
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:5173
pause

