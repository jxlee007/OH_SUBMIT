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

# 1. Python Virtual Environment Setup
echo "[1/4] Checking Python Virtual Environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv..."
    python3 -m venv .venv 2>/dev/null || python -m venv .venv
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

# 2. Backend Dependencies
echo ""
echo "[2/4] Installing backend dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# 3. Database Initialization & Seed Check
echo ""
echo "[3/4] Initializing PostgreSQL database and running seed verification..."
python -m backend.scripts.seed

# 4. Frontend Dependencies
echo ""
echo "[4/4] Installing frontend dependencies..."
cd frontend
if command -v npm.cmd &> /dev/null; then
    npm.cmd install
else
    npm install
fi
cd ..

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

