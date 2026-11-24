# 🎁 Wedding Gift Ledger

> **Intelligent Wedding Gift Management, Note Processing, Thank-You Tracking & Reciprocity Ledger**

A complete, modern, full-stack web application built for **Farhana's Family Wedding** to organize gift collections from ~400 guests, transcribe handwritten notes with AI, track personalized thank-you messages without awkward cash amount mentions, and maintain a permanent reciprocal gift ledger for future family weddings.

---

## 👥 3-Member Team Work Breakdown Structure

This project is partitioned cleanly among **3 Team Members** with distinct boundaries:

| Member | Role | Core Modules & Responsibilities |
| :--- | :--- | :--- |
| **Member 1** | **Backend & Database Architect** | MySQL 8 relational schema, SQLAlchemy ORM, Alembic migrations, Auth/JWT, Guest & Gift CRUD REST APIs, database transactions & soft delete. |
| **Member 2** | **Frontend & UI/UX Design Engineer** | SaaS Design system (Linear/Stripe inspired), CSS Grid/Flexbox responsive layout, HTML5 pages, Vanilla JS modules (`api.js`, `utils.js`), Chart.js integration. |
| **Member 3** | **AI Services, Reciprocity & QA Lead** | AI handwritten note parser (`/api/ai/process-note`), multi-tone Thank-You generator (`/api/thank-you/generate`), Reciprocity comparison ledger, CSV reports, realistic seed data, and Pytest QA suite. |

*Detailed breakdown available in [`docs/TEAM_SPLIT.md`](docs/TEAM_SPLIT.md).*

---

## ⚡ Core Business Principles Enforced

1. **Accuracy is More Important than Guessing:** Never invent missing names, cash amounts, or relationships.
2. **Original Note Preservation:** Raw handwritten notes (e.g., *"Rahman uncle - dinner set"*, *"Shilpi khala + family, envelope"*, *"the people from Chittagong - 2 sarees, didn't catch name"*, *"big box, no card???"*) are preserved permanently.
3. **Strict Thank-You Rule:** Thank-you messages **never mention cash amounts**, even if explicitly recorded in the database.
4. **Joint Gift Support:** A single gift record connects to multiple contributors via relational many-to-many architecture without duplicating gift records.
5. **Reciprocity Ledger:** Tracks gifts received at Farhana's wedding and compares them with gifts given by Farhana's family when attending guests' future weddings without assuming artificial market values.

---

## 🛠️ Technology Stack

* **Frontend:** HTML5, CSS3 (Custom Design System), Vanilla JavaScript (ES6+), Chart.js
* **Backend:** Python 3.14, FastAPI, Pydantic v2, SQLAlchemy 2.0 ORM
* **Database:** MySQL 8 (with fallback to SQLite for offline execution)
* **Migrations:** Alembic
* **Testing:** Pytest (15/15 Passing Automated Tests)

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* Python 3.10+ (Tested on Python 3.14)
* MySQL 8 or XAMPP MariaDB (Running on `localhost:3306`)

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Database Setup & Seeding
Create database and seed with demo records:
```bash
# Seed all 4 assessment prompt cases + realistic wedding data
python scripts/seed_data.py
```

### 4. Start the Application
```bash
# Start FastAPI backend server
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000/`** (or `http://127.0.0.1:8000/dashboard.html`)

**Default Demo Credentials:**
* Username: `admin`
* Password: `admin123`

---

## 🧪 Automated Testing

Run the full automated test suite covering Guest CRUD, Gift CRUD, AI Note Parsing, Strict Thank-You generation, Reciprocity Ledger, and CSV exports:

```bash
python -m pytest backend/tests -v
```

**Results:**
```text
======================= 15 passed in 0.29s =======================
```

---

## 📂 Project Structure

```text
wedding-gift-ledger/
├── frontend/
│   ├── index.html              # Landing & Family Login
│   ├── dashboard.html          # Stats, Charts & Activity
│   ├── guests.html             # Guest Directory & Add/Edit
│   ├── gifts.html              # Gift Records & AI Note Parser
│   ├── thank-you.html          # Thank-You Generator & Tracking
│   ├── ai-assistant.html       # Interactive AI Query Tool
│   ├── gift-history.html       # Reciprocity Ledger
│   ├── reports.html            # Analytics & CSV Export
│   ├── settings.html           # Family & System Settings
│   ├── css/                    # Design System & Responsive Styles
│   └── js/                     # API Client, State & Modules
├── backend/
│   ├── app/
│   │   ├── core/               # Database, Config & Security
│   │   ├── models/             # SQLAlchemy ORM Models
│   │   ├── schemas/            # Pydantic v2 Schemas
│   │   ├── routers/            # FastAPI REST Routers
│   │   ├── services/           # Business Logic & AI Engines
│   │   └── main.py             # FastAPI App Entrypoint
│   └── tests/                  # Pytest Automated Test Suite
├── migrations/                 # Alembic Database Migrations
├── scripts/
│   ├── seed_data.py            # Database Seeder
│   └── start_server.bat        # One-Click Launch Script
├── docs/
│   └── TEAM_SPLIT.md           # 3-Member Responsibilities
└── README.md
```

---

## 📄 License
Academic and Commercial Project License for Farhana's Family Wedding Gift Management.
