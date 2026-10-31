#!/usr/bin/env bash
# ==============================================================================
# Odoo x FLUX Hackathon 2026 - Setup & Stack Launcher
# Works on Linux, macOS, WSL, and Git Bash for Windows
# ==============================================================================

set -e

echo "========================================================"
echo "  Odoo x FLUX Lucknow Hackathon 2026 - Stack Setup      "
echo "========================================================"
echo ""

# 1. Environment Config Setup
if [ ! -f "backend/.env" ] && [ -f "backend/.env.example" ]; then
    echo "[0/4] Creating backend/.env from backend/.env.example..."
    cp backend/.env.example backend/.env
fi

# 2. Python Virtual Environment Setup
echo "[1/4] Checking Python Virtual Environment..."
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv..."
    $PYTHON_CMD -m venv .venv
fi

# Detect activation script (Windows vs POSIX)
if [ -f ".venv/Scripts/activate" ]; then
    # Git Bash on Windows
    source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
    # Linux / macOS / WSL
    source .venv/bin/activate
else
    echo "Warning: Could not find virtualenv activate script. Continuing with system python..."
fi

# 3. Backend Dependencies
echo ""
echo "[2/4] Installing backend dependencies..."
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt --quiet

# 4. Database Initialization & Seed Check (Non-fatal warning if PG is down)
echo ""
echo "[3/4] Initializing PostgreSQL database and running seed verification..."
set +e
python -m backend.scripts.seed
SEED_EXIT_CODE=$?
set -e
if [ $SEED_EXIT_CODE -ne 0 ]; then
    echo "Notice: Database seed could not connect to PostgreSQL."
    echo "        Ensure PostgreSQL is running locally and database 'oh_db' exists,"
    echo "        then run: python -m backend.scripts.seed"
fi

# 5. Frontend Dependencies
echo ""
echo "[4/4] Installing frontend dependencies..."
if command -v npm.cmd &> /dev/null; then
    (cd frontend && npm.cmd install)
else
    (cd frontend && npm install)
fi

echo ""
echo "========================================================"
echo "  Setup Complete! All dependencies & DB verified.       "
echo "========================================================"
echo ""
echo "To run the application:"
echo ""
echo "Terminal 1 (Backend API & DB):"
echo "  source .venv/bin/activate  (or .venv/Scripts/activate on Windows)"
echo "  uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend && npm run dev"
echo ""
echo "Or on Windows, simply run: ./dev.bat"
echo "========================================================"
