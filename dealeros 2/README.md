# DealerOS — Reconciliation Assessment

A small Django + Django REST Framework API and React/Vite screen that imports the supplied CSV ledgers, detects disagreements, and scopes results by tenant organization.

## Requirements
- Python 3.11+
- Node.js 18+
- Git (optional for local run)

## Run from a clean checkout

### 1. Backend
From the repository root:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd backend
python manage.py makemigrations reconcile
python manage.py migrate
python manage.py import_data
python manage.py import_data  # safe repeat; must not create duplicates
python manage.py runserver
```

The API is at `http://127.0.0.1:8000/api/disagreements/?org=ORG-A`.

### 2. Frontend
In a second terminal, from repository root:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (normally `http://localhost:5173`).

### 3. Tests
From repository root with the virtual environment active:

```bash
cd backend
pytest
```

## What is implemented
- Imports all rows from `locations.csv`, `system_a.csv`, and `system_b.csv` into SQLite.
- Uses `update_or_create`, so repeated imports are idempotent.
- Preserves raw B reference and amount text; invalid/blank numeric values become NULL rather than zero.
- Normalizes record references such as `rec1034`, ` REC - 1070 `, and numeric-only references.
- Compares B values with A `total_value` using Decimal.
- Detects missing, orphan, duplicate, blank/wrong value, date, and location disagreements. Valid split entries whose sum equals the A total are accepted.
- Provides organization filter, reason filter, and value sorting in the React table.

## Tenant-safety design
Location-to-org ownership comes only from `locations.csv`. A-side disagreements are scoped to the A record's organization. Orphans are scoped to the organization of their B location. When a matching B entry belongs to a different tenant, the API masks its location as `[other tenant]` instead of exposing that location identifier. The API requires an explicit org parameter and applies organization scoping in database queries before returning rows.

## Deliberate omissions
Authentication, pagination, Docker, deployment hardening, advanced styling, and user management are outside this time-boxed assessment. The demo organization selector is not authentication; production access must derive org identity from an authenticated user/session, not trust a query parameter.

## Decisions
1. **Compare against `total_value`.** B records the final amount, so compare it with A's base plus adjustment, not base alone.
2. **Blank values are unknown.** Store them as NULL and report a value mismatch; never coerce them to zero.
3. **Normalize references but preserve originals.** Keep `record_ref_raw` for audit and use a cleaned `record_ref` for matching.
4. **Treat a multi-entry group as a split only when its sum equals A total.** Otherwise flag it as `DUPLICATE_IN_B`.
5. **VOIDED records.** This implementation still reconciles them against B. A B entry for a voided A record is not automatically hidden; its actual value/date/location differences remain visible. This is an explicit conservative choice pending business confirmation.
6. **Date and location differences count.** They are useful reconciliation discrepancies beyond the four mandatory reasons.
7. **Cross-tenant location mismatch.** Attribute the disagreement to the A-side tenant and mask the other tenant's B location. Orphans use B's own location to determine tenant ownership.
8. **SQLite and Decimal.** SQLite keeps setup simple; Decimal preserves exact currency arithmetic.

## AI-agent work disclosure — personalize before submission
This repository was generated with AI assistance. I reviewed the requirements and supplied CSVs, then used the generated code as a starting point. Before submission, run the tests, inspect the detected disagreements, and be ready to explain the importer, comparison rules, and tenant-scoping code. Replace this paragraph with an accurate account of what you personally changed and verified.

## Required reflection questions — write in your own words
1. **One thing the AI agent got wrong. How did you notice?** Do not invent an example. After reviewing the code/data, describe a real issue you found and the check that exposed it.
2. **The part you are least confident about, and why?** Be honest. A good candidate to review carefully is the cross-tenant mismatch handling and how multiple B entries are grouped.
3. **If you had a second day, what would you fix first?** Name one concrete improvement and explain why it matters.
