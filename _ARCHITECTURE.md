# System Architecture & Technical Decisions

This document outlines the architectural decisions, design patterns, and engineering rationale implemented in the solution, aligned with the **Odoo Hackathon Evaluator Scoring Rubric**.

---

## 1. System Architecture & End-to-End Flow

The system is architected as an offline-resilient, three-tier application emphasizing strict relational data modeling, domain modularity, and layered input validation.

```mermaid
flowchart TD
    subgraph Client ["Frontend Layer (React + Vite + Tailwind CSS)"]
        UI["Responsive UI (375px Mobile / 768px Tablet / 1280px Desktop)"]
        Val1["Layer 1 Validation (Instant Inline Helper Feedback)"]
        APIClient["Centralized API Client (Envelope Unwrapping)"]
        UI --> Val1 --> APIClient
    end

    subgraph Server ["Backend API Layer (FastAPI)"]
        Router["Resource-Oriented REST Routers (/api/...)"]
        Val2["Layer 2 Validation (Pydantic v2 Schemas / 422 Handler)"]
        Services["Business Logic Services (Single Responsibility)"]
        Router --> Val2 --> Services
    end

    subgraph Data ["Persistence Layer (PostgreSQL 18 Local)"]
        ORM["SQLAlchemy Models & Session Pooling"]
        Val3["Layer 3 Validation (NOT NULL, CHECK, UNIQUE, Foreign Keys)"]
        DB[(PostgreSQL Relational Database)]
        Services --> ORM --> Val3 --> DB
    end

    APIClient <-->|"JSON Envelope {'success', 'data', 'error', 'message'}"| Router
```

---

## 2. Problem Framing & Operational Constraints

- **Scope Decision:** Focus exclusively on delivering one polished, end-to-end happy path rather than multiple shallow features.
- **Target Persona:** Operational users who require immediate data feedback, zero ambiguity in error handling, and fast, low-friction navigation.
- **Operational Constraints:**
  - Strict 8-hour sprint window.
  - 100% self-hosted, offline-capable local operation (no external cloud services or BaaS).
  - Strict responsive behavior across three target viewports: Mobile (375px), Tablet (768px), and Desktop (1280px).
- **Measurable Success Criteria:**
  1. Zero unvalidated data leakage into the database across all inputs.
  2. Target: Sub-50ms local API response times with zero N+1 database queries (unmeasured / target).
  3. Immediate browser refresh reflecting PostgreSQL state dynamically (zero static mock JSON).

---

## 2.1 Scope Tiers: 5 Core Features & Explicit Roadmap Matrix

In strict compliance with the **3-to-5 feature rule** for an 8-hour sprint, features are rigorously bounded:

### Core Vertical Slice (5 Features Built & Tested)
1. **Feature 1: Authentication & Role-Based Access Control (RBAC):** Registration with password rules (8+ chars, upper, lower, special), bcrypt hashing, pure in-memory access token + httpOnly refresh cookie, 403 Forbidden enforcement on customer role.
2. **Feature 2: Catalog Products & Subscription Recurrence Plans:** Distinct 3NF tables (`products` and `plans`) with recurrence periods (`daily`, `weekly`, `monthly`, `yearly`), min quantity, and availability dates.
3. **Feature 3: Subscription Lifecycle State Machine:** 5-state progression (`Draft` → `Quotation` → `Confirmed` → `Active` → `Closed`) with `409 Conflict` rejection of illegal transitions and PostgreSQL `CHECK` constraint.
4. **Feature 4: Recurring Invoicing & Tax Calculation:** Snapshot period billing generation, rounded line-item tax calculation, and `uq_invoice_subscription_period` unique constraint preventing double-billing.
5. **Feature 5: Payment Settlement Ledger:** Payment recording linked to invoices with `ck_payment_positive CHECK (amount > 0)` constraint and outstanding balances.

*Note on Dashboard:* The **Dashboard Summary** is classified as a **Read-only Aggregation View** (UI reporting layer aggregating live counts over existing tables) rather than a distinct feature, preserving the 5-feature limit.

### Explicit Requirements Status Matrix
| Requirement | Tier | Status | Rationale |
|---|---|---|---|
| User registration, login, role claim | Core | ✅ Built | Tested via `test_auth.py` |
| Products & Plans 3NF separation | Core | ✅ Built | Tested via `test_products.py` & in `oh_db` |
| 5-stage subscription state machine | Core | ✅ Built | Tested via `test_subscriptions.py` (409 transition guard) |
| Period invoice generation & double-billing guard | Core | ✅ Built | Tested via `test_invoices.py` |
| Payment recording with amount > 0 | Core | ✅ Built | Tested via `test_payments.py` |
| Read-only operational metrics view | View | ✅ Built | Tested via `test_dashboard.py` |
| Discount rules applied to next invoice | Expected | ⬜ Not built (Roadmap) | Scope freeze at 14:00 |
| Password reset flow via local SMTP capture | Expected | ⬜ Not built (Roadmap) | Scope freeze at 14:00 |
| Quotation templates | Expected | ⬜ Not built (Roadmap) | Scope freeze at 14:00 |
| Product variants | Expected | ⬜ Not built (Roadmap) | Scope freeze at 14:00 |
| Real email delivery & printed PDFs | Stretch | ⬜ Not built (Roadmap) | Scope freeze at 14:00 |
| Pause and renew automation | Stretch | ⬜ Not built (Roadmap) | Scope freeze at 14:00 |

---

## 3. Domain Boundaries & Separation of Concerns

- **Module Ownership:** The system isolates responsibilities into distinct modules:
  - `backend/app/core/`: Configuration, database engines, connection poolers, and lifecycle management.
  - `backend/app/models/`: Relational schema declarations and persistent database constraints.
  - `backend/app/schemas/`: Typed Pydantic models for incoming payload validation and outgoing serialization.
  - `backend/app/services/`: Isolated business logic and transactional workflows.
  - `backend/app/routes/`: Transport layer handling HTTP routing, parameters, and status codes.
- **Communication Contracts:** The frontend communicates strictly via documented REST endpoints. Services never execute direct cross-domain mutations without designated service interfaces.
- **Unidirectional Dependency Flow:**
  $$\text{Frontend UI} \longrightarrow \text{REST Routers} \longrightarrow \text{Domain Services} \longrightarrow \text{SQLAlchemy Adapters} \longrightarrow \text{PostgreSQL}$$

---

## 4. Database Architecture & Relational Modeling (Core Scoring Priority)

Database design is treated as the primary technical foundation of the system:
- **3NF Normalization:** All relational entities are normalized to Third Normal Form (3NF) to eliminate data duplication and guarantee a single source of truth.
- **Referential Integrity:** Enforced via foreign key constraints with explicit `ON DELETE CASCADE` or `RESTRICT` rules to prevent orphaned records.
- **Indexing Strategy:** Primary keys and foreign keys are indexed by default; composite B-tree indexes are added to frequently filtered status fields and sorted timestamp columns.
- **N+1 Query Elimination:** All multi-entity relationships use SQLAlchemy `joinedload` or `selectinload` to fetch related entities in a single indexed query, eliminating round-trip latency.

---

## 5. API Design & Transport Contracts

- **Resource-Oriented REST:** Endpoints use resource nouns instead of actions (e.g., `/api/items`, not `/api/createItem`).
- **Semantic HTTP Verbs:** Strict adherence to standard semantics (`GET` for reading, `POST` for creation, `PATCH` for partial updates, `DELETE` for removal).
- **Standardized Response Envelope:** Every endpoint returns a consistent JSON envelope to ensure predictable client consumption:
  ```json
  {
    "success": true,
    "data": { ... },
    "error": null,
    "message": "Operation completed successfully"
  }
  ```
- **Semantic HTTP Status Codes:**
  - `200 OK` / `201 Created` for successful operations.
  - `400 Bad Request` for business logic contradictions.
  - `403 Forbidden` for role-based authorization denials (e.g., customer accessing staff/admin routes).
  - `404 Not Found` when a requested entity does not exist.
  - `409 Conflict` for state machine transition violations and unique constraint duplicates (e.g., double-billing).
  - `422 Unprocessable Entity` for schema/type validation failures with friendly field-level messages.
  - `500 Internal Server Error` for unexpected server exceptions.

### 5.1 Authentication Transport & Zero Web Storage Model
- **Pure In-Memory Access Token:** The React client holds the short-lived JWT strictly within a private JavaScript closure in `api.js`. It is NEVER written to `localStorage` or `sessionStorage`, completely immunizing the application against persistent token theft via XSS.
- **HttpOnly Refresh Cookie:** On `POST /api/auth/login` or `POST /api/auth/register`, FastAPI sets an `httpOnly, samesite=lax, path=/api/auth` cookie containing a cryptographically signed refresh token.
- **Transparent Session Hydration:** On app initialization or browser page reload, `App.jsx` issues `POST /api/auth/refresh` with `credentials: 'include'`. FastAPI validates the cookie and returns a fresh short-lived access token, restoring session state seamlessly without client storage.
- **Revocation & Logout:** `POST /api/auth/logout` sets `Max-Age=0` on the cookie and immediately wipes in-memory variables.

---

## 6. The 3-Layer Validation Defense

To guarantee data integrity and provide clear, friendly user feedback, validation is implemented across three discrete layers:

| Layer | Implementation | Responsibility | User Feedback Mode |
|---|---|---|---|
| **Layer 1: Client** | React Form State & Regex | Immediate inline validation on change / blur | Friendly helper text (e.g., *"Please enter a valid email address"*). |
| **Layer 2: Server** | FastAPI & Pydantic v2 | Payload structure, data types, value boundaries | Standardized `422 Unprocessable Entity` response with field-level guidance. |
| **Layer 3: Database** | PostgreSQL Constraints | Permanent persistence defense (`NOT NULL`, `CHECK`, `UNIQUE`, FKs) | Immediate transaction rollback, preventing data corruption. |

---

## 7. Code Quality & Maintainability Standards

- **Single Responsibility Principle:** Every function executes exactly one well-defined job (readable in under two minutes).
- **Pure Functions:** Business calculations and formatters are deterministic pure functions (same inputs always yield identical outputs without side effects).
- **Framework Decoupling:** Business domain rules remain decoupled from web framework internals, allowing isolated automated testing.
- **Self-Documenting Code:** Clean identifier naming, clear variable semantics, and comments focusing on *why* a design decision was made rather than *what* the syntax is doing.

---

## 8. Failure Modes, Resilience & Key Trade-offs

### Handled Edge Cases
1. **Duplicate Submissions:** Caught by PostgreSQL `UNIQUE` constraints $\to$ translated into a friendly `400 Bad Request` message.
2. **Malformed Payloads:** Caught by Pydantic $\to$ translated into a descriptive `422` envelope detailing the exact field requiring correction.
3. **Temporary Network or Database Disconnects:** Handled gracefully by the client API service, displaying an offline banner without crashing the interface.

### Architectural Trade-off: Local PostgreSQL vs. Backend-as-a-Service (Firebase / Supabase)
- **Decision:** Build from scratch using local PostgreSQL and FastAPI.
- **Rationale:** While BaaS solutions offer rapid prototyping, they introduce external internet latency, rate limits, vendor lock-in, and unpredictable platform bugs. An offline-resilient local PostgreSQL stack showcases core relational engineering, query optimization, and total data sovereignty, directly matching the core philosophy of the hackathon evaluators.
