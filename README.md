# Odoo x FLUX Lucknow Hackathon 2026 | Virtual Round

**Team Leader:** Jagmohan Singh Malhi (`JAGMOHAN`)  
**Evaluator:** Piyush Soni (`piso@odoo.com`) | GitHub: `piso-odoo`, `hackathon-odoo`  
**Duration:** 8 Hours (9:00 AM – 5:00 PM, Oct 31, 2026)  

---

# Brightloop Subscription Management System

A unified, offline-resilient platform running products, recurring plans, subscription lifecycle state machines, automated period invoicing with taxes, and payment settlements against local PostgreSQL.

---

## 1. Problem Statement & Context

**Brightloop Software** sells software licenses, platform add-ons, and recurring enterprise services billed on daily, weekly, monthly, and yearly cycles. Previously:
- Customer subscriptions were tracked in disparate spreadsheets.
- Renewals were remembered only by whoever noticed first.
- Invoices were manually typed each billing period, creating calculation mistakes.
- Payments were matched by manually scrolling bank statements.
- Revenue numbers took days to reconcile at the end of each quarter.

This platform replaces that manual workflow with an offline-first, dynamic REST API and responsive React interface powered exclusively by local PostgreSQL—with zero reliance on external BaaS (Firebase/Supabase).

---

## 2. System Architecture Overview

Brightloop is built with an **offline-first local PostgreSQL architecture** (zero cloud BaaS), strict 3NF entity normalization, and a 3-layer validation defense model.

For full architectural blueprints, entity-relationship schemas, state diagrams, security protocols, and concurrency locking mechanisms, refer to the dedicated architecture specification:  
👉 **[Full Architecture Documentation (_ARCHITECTURE.md)](_ARCHITECTURE.md)**

### Key Architectural Highlights
- **Products vs. Plans Decoupling:** 3NF normalized schema separates catalog products from recurring billing plans with pricing and period rules.
- **5-State Subscription Lifecycle:** `draft` → `quotation` → `confirmed` → `active` → `closed` with `paused` capability and 409 transition guards.
- **3-Layer Validation Defense:** Client-side inline regex → Pydantic v2 server constraints (422/409) → PostgreSQL schema integrity (`CHECK`, `UNIQUE`, FKs).
- **Zero Web Storage Security:** Pure in-memory JWT access tokens coupled with secure `httpOnly, SameSite=Lax` refresh cookies.
- **Concurrency Locking:** Atomic row-level locking (`SELECT ... FOR UPDATE` + process mutex) preventing promotional discount limit overruns under multi-threaded races.
- **Pure PDF Presentation Engine:** ReportLab-powered invoice rendering (`GET /api/invoices/{id}/pdf`) with stored amounts, zero DB access, and a 1-page layout guarantee.

---

## 3. Requirements & Scope Matrix

In strict compliance with the **3-to-5 feature rule** for an 8-hour sprint, features are rigorously bounded to 5 Core Features + 1 Read-only Aggregation View:

### Core Vertical Slice (Built & Verified — 5 Features + 1 View)
| Feature | Tier | Status | Verification |
|---|---|---|---|
| Registration with unique email & password policy (8+ chars, upper, lower, special) | Core | ✅ Built | Tested via `test_auth.py` |
| Role-based access control (`admin`, `staff`, `customer`) & privilege protection | Core | ✅ Built | Tested via `test_auth.py` (only admin adds staff -> 403), `test_products.py`, `test_subscriptions.py`, `test_payments.py` (403 assertions) |
| Customer data scoping (customers only access own subscriptions and invoices) | Core | ✅ Built | Tested via `test_subscriptions.py` (403) and `test_invoices.py` (403) |
| Products & Plans separation with billing periods (`daily`, `weekly`, `monthly`, `yearly`) | Core | ✅ Built | Tested via `test_products.py` & verified in `oh_db` |
| Subscription 5-state lifecycle (`draft` → `quotation` → `confirmed` → `active` → `closed`) with 409 transition guard | Core | ✅ Built | Tested via `test_subscriptions.py` |
| Period invoice generation with per-line tax & half-up rounding | Core | ✅ Built | Tested via `test_invoices.py` |
| Double-billing prevention per period (`uq_invoice_subscription_period`) | Core | ✅ Built | Tested via `test_invoices.py` |
| Invoice lifecycle transitions (draft/confirmed to cancelled, 409 guard preventing cancellation of paid invoices) | Core | ✅ Built | Tested via `test_invoices.py` (`test_cancel_draft_or_confirmed_invoice_happy_path`, `test_cancel_paid_invoice_returns_409`) |
| Invoice PDF download via ReportLab (pure function, stored amounts, 1-page 5-line layout) | Core (Invoicing) | ✅ Built | Tested via `test_pdf.py` (5 tests passing: `%PDF`, pypdf text inspection, 1-page layout, customer 403 scoping, 404 on unknown invoice) |
| Payment recording against invoices with `ck_payment_positive` (`amount > 0`) | Core | ✅ Built | Tested via `test_payments.py` |
| Real-time operational dashboard with KPI metrics (Read-only UI aggregation) | View | ✅ Built | Tested via `test_dashboard.py` (No state mutations) |

### Expected & Stretch Features (Incrementally Built & Tested)
| Requirement | Tier | Status | Specification & Verification |
|---|---|---|---|
| Discount rules applied to next invoice | Expected | ✅ Built | Tested via `test_discounts.py`: Admin CRUD, concurrency row locking (`SELECT ... FOR UPDATE` + process mutex) verified via multi-threaded race test (201 vs 409), invoice line-item storage, expired 400, limit 409, percent > 100 422. |
| Password reset flow | Expected | ✅ Built | Tested via `test_password_reset.py`: Anti-enumeration 200, SHA-256 single-use tokens, 30-min expiry 400, reused 400, password policy 422, `token_version` session revocation verified (old tokens rejected with 401 Unauthorized), offline capture sink. |
| Quotation templates | Expected | ✅ Built | Tested via `test_quotation_templates.py`: Bundle creation with line items, validity days check, 1-click instantiate to draft subscription, 409 guard on expired quote confirmation. |
| Product variants | Expected | ✅ Built | Tested via `test_product_variants.py`: Attributes & values, unique SKU, price delta calculation (base + delta), and subscription line item referencing. |
| Pause and renew automation | Stretch | ✅ Built | Tested via `test_scheduler_and_pause.py`: In-process APScheduler daily billing engine, plan can_pause/can_renew capabilities, automatic skipping of paused subscriptions, admin manual execution route, and scheduler lifecycle tested. |
| Admin-configured dynamic tax rules | Stretch | ⬜ Not built (Roadmap) | Dynamic multi-jurisdiction tax rule matrix. Currently enforced via explicit per-line tax rates and stored invoice values. |
| Send invoice via email | Stretch | ⬜ Not built (Roadmap) | External SMTP relay delivery of invoice notification emails. |

---

## 4. Performance Targets & Measured Benchmarks

In compliance with the Hackathon Agent Rules ("Strict Metric Rule — no number appears in documentation or demo unless a command printed it during the sprint"):

- **Specification Target:** Page load and query response under 2.0 seconds with thousands of subscriptions.
- **Measured Dataset in Local PostgreSQL (`oh_db`):** **2,502 Subscriptions, 5,001 Invoices**.
- **Benchmark Script:** `backend/scripts/benchmark_large_dataset.py`

#### Live Wall-Clock Query Benchmark Results:
| Query Operation | Dataset Scope | Measured Wall-Clock Time | Evaluator Target | Margin |
|---|---|---|---|---|
| **Dashboard KPI Aggregation** | 5,001 invoices (SUM, COUNT) | **7.93 ms** | < 2,000 ms | **252.3x faster** |
| **Customer Subscriptions Lookup** | Customer filter + plan JOINs | **7.99 ms** | < 2,000 ms | **250.3x faster** |
| **Paginated Invoices Listing** | `LIMIT 50 OFFSET 100` | **15.30 ms** | < 2,000 ms | **130.7x faster** |
| **Overdue Invoices Scan** | Top 100 scan ordered by due date | **9.24 ms** | < 2,000 ms | **216.4x faster** |

#### Live PostgreSQL `EXPLAIN ANALYZE` Index Proof:
```sql
-- 1. Customer Subscriptions Lookup (Bitmap Index Scan on ix_subscriptions_customer_id)
Bitmap Heap Scan on subscriptions  (cost=4.30..13.45 rows=3 width=110) (actual time=0.078..0.081 rows=3 loops=1)
  ->  Bitmap Index Scan on ix_subscriptions_customer_id (cost=0.00..4.30 rows=3) (actual time=0.043..0.043 rows=3 loops=1)
Planning Time: 0.336 ms | Execution Time: 0.103 ms

-- 2. Double-Billing Period Guard (Index Scan using uq_invoice_subscription_period)
Index Scan using uq_invoice_subscription_period on invoices (cost=0.28..8.30 rows=1) (actual time=0.102..0.104 rows=1 loops=1)
Planning Time: 0.227 ms | Execution Time: 0.131 ms

-- 3. Invoices by Customer ID (Bitmap Index Scan on ix_invoices_customer_id)
Bitmap Heap Scan on invoices  (cost=4.33..22.94 rows=6 width=90) (actual time=0.044..0.048 rows=6 loops=1)
  ->  Bitmap Index Scan on ix_invoices_customer_id (cost=0.00..4.33 rows=6) (actual time=0.014..0.015 rows=6 loops=1)
Planning Time: 0.187 ms | Execution Time: 0.069 ms
```

---

## 5. Fast Evaluator Demo Credentials

Pre-seeded into local PostgreSQL (`oh_db`):

| Role | Email | Password | Allowed Capabilities |
|---|---|---|---|
| **Admin** | `admin@brightloop.com` | `Admin@1234` | Full system control: create products, plans, subscriptions, invoices, and payments. |
| **Staff** | `staff@brightloop.com` | `Staff@1234` | Operational access: subscriptions, invoices, and payment recording. |
| **Customer** | `customer@brightloop.com` | `Customer@1234` | Portal subscriber: view own subscriptions and invoices only (admin routes return `403 Forbidden`). |

---

## 6. Setup & Local Run Instructions

### 1. Backend Setup (FastAPI + Local PostgreSQL)
```powershell
# Ensure PostgreSQL is running locally and database oh_db is created
cd a:\SAAS\OH_SUBMIT

# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run demo database seeding (idempotent)
python backend/scripts/seed.py

# Run automated test suite (92 tests)
pytest backend/tests/ -v

# Run large-dataset scalability benchmark & EXPLAIN ANALYZE index proof
python backend/scripts/benchmark_large_dataset.py
```

#### Live Test Suite Terminal Output (Verified 92/92 Passing)
The complete unedited terminal test run output (92 passed in pytest) is archived at [`docs/test_output.text`](docs/test_output.text).

# Start backend server (Port 8000)
```powershell
uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend Setup (React + Vite + Tailwind)
```powershell
cd a:\SAAS\OH_SUBMIT\frontend

# Install dependencies
npm install

# Start Vite development server (Port 5173)
npm run dev
```

### 3. Verify in Browser
- Open `http://localhost:5173`
- Click any Evaluator Fast-Login pill on `/login` to explore each role's view.
- Responsive breakpoints verified at `375px` (mobile), `768px` (tablet), and `1280px` (desktop).

---

**Built by:** Jagmohan Singh Malhi (`JAGMOHAN`)
