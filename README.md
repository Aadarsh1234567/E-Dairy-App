# Santosh E-Dairy — Development Setup

## Phase 1 + Phase 2: Foundation & Database Layer

---

## Requirements

- Python 3.11 or 3.13+
- Windows 10/11 (final packaged .exe target)
- Works on Linux/Mac for development

---

## Setup (First Time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main.py
```

The database file `dairy_management.db` is created automatically in the
project root on first launch.

---

## Project Structure

```
dairy_management/
├── main.py                  ← Entry point
├── constants.py             ← Colours, theme, stylesheet
├── requirements.txt
├── dairy_management.db      ← Created on first run (not in repo)
│
├── database/
│   ├── models.py            ← All 11 SQLAlchemy ORM models
│   └── database.py          ← Init, seeding, session, audit log
│
├── ui/
│   ├── main_window.py       ← Main window + sidebar navigation
│   └── dashboard/
│       └── dashboard_page.py ← Dashboard with stat cards
│
├── modules/                 ← Business logic (Phase 3+ onwards)
│   ├── auth/
│   ├── farmers/
│   ├── products/
│   ├── transactions/
│   ├── payments/
│   ├── inventory/
│   ├── reports/
│   └── settings/
│
├── services/                ← Pricing, backup, audit, report services
├── exports/                 ← Generated Excel/PDF files
├── backups/                 ← Database backup files
├── assets/
│   └── fonts/
│       └── NotoSansDevanagari.ttf   ← Nepali Unicode font
└── tests/
```

---

## What Is Built (Phase 1 + 2)

### Phase 1 — Foundation
- [x] Application launches as a desktop window
- [x] Branded splash screen
- [x] Sidebar navigation framework
- [x] Dashboard with 5 stat cards (live data-ready)
- [x] Quick action buttons (navigate to future modules)
- [x] Recent transactions table
- [x] Live clock in status bar
- [x] Database connection status indicator
- [x] Version number displayed

### Phase 2 — Database Layer
- [x] All 11 tables created with correct columns and types
- [x] All foreign key constraints
- [x] All CHECK constraints (status values, quantity > 0, etc.)
- [x] Database-level UNIQUE constraint on milk duplicate prevention
- [x] All 8 required indexes
- [x] Schema version tracking (schema_versions table)
- [x] Auto-migration framework on startup
- [x] Default products seeded (Milk, Butter, Paneer, Ghee, Cheese, Curd)
  — with bilingual Nepali names
- [x] Default settings seeded (org name, formula, language, version)
- [x] Initial pricing formula seeded: (fat*8)+(snf*4)
- [x] Audit log with SHA-256 tamper-detection chain
- [x] Backup path resolved (D:\ or Documents fallback)
- [x] Noto Sans Devanagari font bundled and verified

---

## Database Tables Built

| # | Table                   | Purpose                          |
|---|-------------------------|----------------------------------|
| 1 | farmers                 | Farmer records (bilingual)       |
| 2 | products                | Dairy products (bilingual)       |
| 3 | transactions            | All product transactions         |
| 4 | milk_details            | Milk-specific data + formula     |
| 5 | payments                | Farmer payments + receipt number |
| 6 | inventory_movements     | Stock in/out tracking            |
| 7 | settings                | System configuration             |
| 8 | pricing_formula_history | Formula versions with dates      |
| 9 | audit_logs              | Tamper-chained action log        |
|10 | backups                 | Backup history + verification    |
|11 | schema_versions         | Migration tracking               |

---

## Next Phase

**Phase 3 — Authentication Module**
- Login screen
- Password hashing (bcrypt)
- Failed-attempt lockout (3 attempts → 5 min lock)
- Idle screen lock (15 min)
- Force password change on first login
