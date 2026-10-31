@echo off
TITLE Brightloop SaaS - Development Stack Launcher
echo ========================================================
echo   Odoo x FLUX Lucknow Hackathon 2026 - Stack Launcher
echo ========================================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment .venv not found.
    echo Please run setup.sh or create .venv first.
    pause
    exit /b 1
)

echo [1/2] Launching Backend API (Port 8000)...
start "Brightloop Backend (FastAPI)" cmd /k "call .\.venv\Scripts\activate.bat && uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"

echo [2/2] Launching Frontend (Port 5173)...
start "Brightloop Frontend (Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo Both Backend and Frontend services launched!
echo - Backend API:  http://127.0.0.1:8000
echo - Swagger Docs: http://127.0.0.1:8000/docs
echo - Frontend UI:  http://localhost:5173
echo ========================================================

