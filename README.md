# Odoo x FLUX Lucknow Hackathon 2026 | Virtual Round

**Team Leader:** Jagmohan Singh Malhi (`JAGMOHAN`)  
**Evaluator:** Piyush Soni (`piso@odoo.com`) | GitHub: `piso-odoo`, `hackathon-odoo`  
**Duration:** 8 Hours (9:00 AM – 5:00 PM, Oct 31, 2026)  

---

# [Project Title]

## Problem Statement
[Selected on 31 Oct, 08:30 AM: 1-2 sentences on what problem this solves]

## Solution & Key Features
- **Core Feature:** [Primary flow]
- **3-Layer Validation:** Client + Server (Pydantic) + Database (PostgreSQL constraints)
- **Responsive UI:** Tested for 375px (mobile), 768px (tablet), and 1280px (desktop)

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** React + Vite + Tailwind CSS (Responsive Design Tokens)
- **Database:** PostgreSQL (Local)
- **ORM / Migrations:** SQLAlchemy

## Architecture
For detailed architectural design decisions, data flow diagrams, and validation models, see [_ARCHITECTURE.md](_ARCHITECTURE.md).

## Folder Structure
```text
OH_SUBMIT/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Loads environment variables, secrets, and defines allowed CORS origins.
│   │   │   └── database.py        # Manages SQLAlchemy connection pooling, session lifecycle, and live health pings.
│   │   ├── models/
│   │   │   └── base.py            # Provides declarative Base and automated created_at/updated_at timestamp mixins.
│   │   ├── schemas/
│   │   │   └── common.py          # Enforces the standardized JSON response envelope across all API endpoints.
│   │   ├── routes/
│   │   │   └── health.py          # Exposes system and PostgreSQL connectivity status check endpoints.
│   │   ├── services/              # Houses isolated, framework-independent business logic and transactional operations.
│   │   └── main.py                # Initializes FastAPI, registers middleware, and formats validation errors into user-friendly messages.
│   ├── scripts/
│   │   └── seed.py                # Idempotently initializes database tables and populates dynamic seed data for demonstrations.
│   ├── tests/
│   │   └── test_health.py         # Automates endpoint verification and database connectivity assertions.
│   ├── requirements.txt           # Pins exact backend dependency versions for reproducible local builds.
│   └── .env.example               # Documents template environment variables required for local PostgreSQL connection.
├── frontend/
│   ├── src/
│   │   ├── components/            # Contains modular, reusable UI components adhering to design tokens.
│   │   ├── pages/                 # Houses top-level application views and full-screen page layouts.
│   │   ├── services/
│   │   │   └── api.js             # Centralizes HTTP requests, standardizes response unwrapping, and intercepts errors.
│   │   ├── App.jsx                # Serves as the root React layout featuring live database status indicators and validation demos.
│   │   ├── index.css              # Imports Tailwind directives and declares core CSS custom property design tokens.
│   │   └── main.jsx               # Mounts the root React component tree into the DOM.
│   ├── tailwind.config.js         # Configures responsive viewport breakpoints (375px, 768px, 1280px) and theme colors.
│   ├── vite.config.js             # Configures fast HMR dev server and proxies /api network requests to port 8000.
│   └── package.json               # Defines frontend scripts and pins dependencies including React, Tailwind CSS, and Lucide icons.
├── setup.sh                       # Automates complete virtual environment, database, and dependency installation across Linux, macOS, and Git Bash.
├── _ARCHITECTURE.md               # Details system design, database normalization, 3-layer validation, and architectural trade-offs.
├── AGENTS.md                      # Establishes competition guidelines, evaluator scoring rubrics, and development timeline protocols.
├── SESSION_LOG.md                # Maintains a chronological one-sentence audit log of all sprint actions, changes, and commits.
└── README.md                      # Provides project overview, setup guides, and quick-start instructions for evaluators.
```

## Setup & Local Run Instructions

### Automated Setup
```bash
# Works on Linux, macOS, WSL, and Git Bash:
chmod +x setup.sh && ./setup.sh
```

### Manual Step-by-Step Setup
```bash
# 1. Clone repository
git clone <repo-url>
cd OH_SUBMIT

# 2. Virtual environment setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Database setup (PostgreSQL local)
# Update DATABASE_URL in backend/.env if needed
python -m backend.scripts.seed

# 5. Start Backend API
uvicorn backend.app.main:app --reload --port 8000

# 6. Start Frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

## Demo Video
- **Public Video Link:** [TBS - Submit by Oct 31, 5:30 PM]

---
**Built by:** Jagmohan Singh Malhi