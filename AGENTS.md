# Virtual Round Agent Rules (Oct 31, 8 hours, Solo)

## Event & Evaluator Profile
- **Event:** Odoo x FLUX Lucknow Hackathon '26 | Virtual Round (8 Hours)
- **Team Leader:** Jagmohan Singh Malhi (`JAGMOHAN`)
- **Evaluator:** Piyush Soni (`piso@odoo.com`) | GitHub: `piso-odoo`, `hackathon-odoo`
- **Critical Checkpoint:** **31 Oct, 10:00 AM** — Add both GitHub handles & email as collaborators.
- **Official Schedule:** 08:30 AM (Problem Selection) -> 09:00 AM (Code Starts) -> 02:00 PM (Feature Freeze) -> 05:00 PM (Code Ends) -> 05:30 PM (Video Submit).

---

## 1. Honesty & Metrics
- **Strict Metric Rule:** No number appears in code, docs, or demo unless a command printed it during the sprint.
- **Never Fabricate Benchmarks:** Zero simulated `EXPLAIN ANALYZE` runtimes (e.g. `0.042ms`), queries/sec, or memory figures.
- **Label Targets Honestly:** Write *"Target: sub-50ms local API response"* or *"To verify: run EXPLAIN ANALYZE to confirm Index Scan"*. Never label unmeasured projections as *"Proven"* or *"Measured"*. All performance numbers in the demo must be voiced strictly as targets unless printed on screen.

---

## 2. Hackathon Must-Haves (Gate for Every Feature)
Every sprint feature must directly serve a must-have from the official evaluator briefing:
1. **Dynamic Data Only:** Local PostgreSQL via REST API (zero static JSON, zero cloud BaaS like Firebase/Supabase).
2. **3-Layer Input Validation:** Client-side inline helper feedback, server-side Pydantic 400/422 validation, and database constraints.
3. **Clean, Responsive UI:** Strict breakpoints at `375px` (mobile), `768px` (tablet), `1280px` (desktop) using CSS design tokens.
4. **Intuitive Navigation:** Proper menu hierarchy, clean spacing, and strict compliance with the 3-click rule.
5. **Git Discipline:** Semantic commits every hour; no end-of-sprint dumps. Developer confirms hourly commits at 10, 11, 12, 1, 2, 3, 4, 5.
*Gate Rule:* If a proposed feature does not directly support one of these must-haves, cut it first.

---

## 3. Sprint Scope vs. Roadmap
- **Design Schema Once (Planning):** Design the complete 3NF normalized schema (all 7–10 tables, foreign keys, constraints, and audit triggers) upfront so the entire product roadmap is supported without future destructive migrations.
- **Build Vertical Slice (Timebox):** An 8-hour solo sprint can only build, validate, and test 3 to 5 core features. Choose these strictly from the Core tier of the requirements matrix at 08:30 AM. Hackathon must-haves always take priority over roadmap breadth.
- **Explicit Requirements Matrix:** In documentation, explicitly tag every requirement as either `✅ Built` or `⬜ Not built (Roadmap)`. Never leave status ambiguous.
- **Scope Coherence (No Silent Re-introductions):** If a feature is marked roadmap-only (e.g. balance sheets, multi-warehouse sync), keep it strictly out of the sprint code, hourly breakdown, and live demo.
- **Stop Rule (Hour 5 Freeze):** At 02:00 PM, feature freeze is absolute. If a feature is broken at Hour 5, state it honestly and remove it from the demo rather than patching the demo around it.

---

## 4. Testing, Commits & Definition of Done
- **Test Rule (Every Feature):** Each feature requires at least 1 happy-path test and at least 1 failure test (400, 403, 409, or 422) asserting the standard response envelope before being marked done.
- **Done Means Tested:** A feature is not done until tests pass (`pytest -v`) and failure paths are logged.
- **Observability & Logs:** Log every caught error with timestamp, level, route, error type, and request ID to console and `logs/app.log`. Never use silent `except: pass`. Global exception handler returns standard envelopes without raw stack traces.
- **Continuous Session Audit Log:** After every chat response, code change, or commit, append a timestamped 1-sentence summary entry to `SESSION_LOG.md` to maintain an unbroken log history of all actions.
- **Commit Cadence:** Commit hourly with semantic messages (`feat(models): ...`, `fix(validation): ...`). The agent drafts and suggests the commit message; the developer runs git commit (no automated commits).

---

## 5. Domain Consistency (Enums, Currency, Timezone)
- **Canonical Enum Single Source of Truth:** Define entity state enums once in models/schemas and enforce uniformly across DB, API, and UI. Never let states drift (e.g. `NEEDS_MAINTENANCE` vs `MAINTENANCE`).
- **Strict Locale & Currency Pairing:** Currency symbols and timezones must reflect a single operational context (e.g. `IST` / `Asia/Kolkata` paired exclusively with `₹` / INR). Never mix currencies (`$` vs `₹`).

---

## 6. Storage Defense & Immutability
- **Two-Layer Defense:** Enforce business invariants in application logic (Pydantic / services for friendly user feedback) AND in the PostgreSQL engine (`CHECK`, `UNIQUE`, foreign keys with `ON DELETE` rules, and triggers for concurrency defense).
- **Canonical Interval Semantics:** When modeling schedule windows with PostgreSQL `tsrange`, always use canonical `[)` half-open intervals (start inclusive, end exclusive) to prevent false conflicts on back-to-back bookings.
- **Audit Immutability vs. State Mutation:** Keep mutable operational states in dedicated tables; maintain separate append-only audit ledgers guarded by PostgreSQL triggers that reject all `UPDATE` and `DELETE` queries.
- **Accounting & Ledger Immutability (Domain-Specific):** For financial/inventory ledgers, never soft-delete or update posted lines. Corrections strictly generate compensating reversing journal entries (with stock adjustments where applicable).

---

## 7. Demo & Closing Claims
- **Demo Rule:** Only demonstrate what is built and tested. If fewer than 3 features are built, demo shows those only; everything else is articulated as roadmap.
- **Honest Closer:** Never claim all roadmap requirements were built in 8 hours. The closer must state:
  > *"In this 8-hour sprint, I built the core vertical slice of [Feature], supported by a complete 3NF schema designed once to accommodate all roadmap requirements without future migrations."*
- **5-Minute Demo Walkthrough (Strict 300s):**
  1. **Executive Overview (0:00–0:40 | 40s):** Problem statement, operational persona, offline-first stack rationale (local PostgreSQL over BaaS).
  2. **Core Flow & Dynamic Data (0:40–1:55 | 75s):** Happy path execution with live DB persistence (browser refresh proving dynamic queries).
  3. **3-Layer Validation Defense (1:55–3:00 | 65s):** Live error triggers across Client (friendly warning) -> Server (Pydantic 422) -> Database constraints.
  4. **Responsive UI & Navigation (3:00–3:50 | 50s):** Live inspection at 375px (mobile), 768px (tablet), 1280px (desktop), verifying 3-click rule.
  5. **Architecture & Schema Defense (3:50–4:35 | 45s):** Defending 3NF normalization, indexed lookups, zero N+1 queries, and audit ledgers (voicing performance as targets).
  6. **Code Tour & Wrap-up (4:35–5:00 | 25s):** Clean code (single responsibility) and hourly git commit history.
