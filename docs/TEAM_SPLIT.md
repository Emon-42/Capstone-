# 👥 Team Work Breakdown Structure (3-Member Project Division)
## Project: Wedding Gift Ledger (SE 331 Software Engineering Project)

To ensure professional collaboration, clear accountability, and balanced workload distribution among **3 team members**, the project was divided into three specialized engineering domains:

---

### 👤 Member 1: Backend & Database Architect
**Primary Responsibilities:**
* **Database Architecture & ORM:**
  * Normalized relational database design on MySQL 8.
  * SQLAlchemy ORM entity mapping: `users`, `wedding_events`, `guests`, `gifts`, `gift_contributors`, `thank_you_messages`, `thank_you_status_history`, `gift_exchange_history`, and `settings`.
  * Alembic migration configuration and version tracking (`migrations/versions/001_initial_schema.py`).
  * Referential integrity, soft deletion design (`is_deleted=True`), and cascade safety to prevent accidental data loss.
* **Core API Development (FastAPI):**
  * Authentication & Session management (`routers/auth.py`, PBKDF2-HMAC-SHA256 password hashing, JWT bearer tokens).
  * Guest CRUD REST APIs (`routers/guests.py`, `services/guest_service.py`).
  * Gift CRUD REST APIs (`routers/gifts.py`, `services/gift_service.py`).
  * Contributor & Joint Gift APIs (`routers/contributors.py`, `services/contributor_service.py`).
* **Backend Testing:**
  * Pytest test suites: `test_guests.py`, `test_gifts.py`.

---

### 👤 Member 2: Frontend & UI/UX Design Engineer
**Primary Responsibilities:**
* **Design System & Visual Architecture:**
  * Created custom SaaS design system inspired by Linear, Stripe Dashboard, and Notion.
  * Theme styling: Warm ivory background (`#fcfbf9`), clean cards (`#ffffff`), deep navy typography (`#0f172a`), elegant purple brand accents (`#5c55d9`), and subtle warm gold highlights (`#c28829`).
  * CSS Grid & Flexbox responsive architecture for desktop, tablet, and mobile devices (`frontend/css/style.css`, `dashboard.css`, `responsive.css`).
* **Frontend Application Pages (Vanilla ES6+ JS & HTML5):**
  * `index.html` (Landing & Family login portal).
  * `dashboard.html` & `dashboard.js` (Dynamic statistics cards, recent activity timeline, Chart.js integrations).
  * `guests.html` & `guests.js` (Guest directory, search, filter, identification badges, add/edit modal).
  * `gifts.html` & `gifts.js` (Master gift ledger, handwritten note callout boxes, cash indicators, joint contributors).
  * `settings.html` & `settings.js` (Family name, wedding name, preferred currency, signature, system health indicators).
* **Client Architecture:**
  * Centralized Fetch API client (`api.js`), toast notification alerts, modal transitions, and debounce utilities (`utils.js`).

---

### 👤 Member 3: AI Engineer, Reciprocity & QA Lead
**Primary Responsibilities:**
* **AI Note Processing Engine (`/api/ai/process-note` & `services/ai_service.py`):**
  * Natural language processing pipeline for handwritten wedding notes (e.g., *"Rahman uncle - dinner set"*, *"Shilpi khala + family, envelope"*, *"the people from Chittagong - 2 sarees, didn't catch name"*, *"big box, no card???"*).
  * Uncertainty flags, missing field detection, confidence scoring, and modal review confirmation.
  * Strict business rule enforcement: NEVER hallucinate cash amounts or identities.
* **Thank-You Message Intelligence (`services/thank_you_service.py` & `frontend/thank-you.html`):**
  * Personalized multi-tone generation (Formal, Warm, Friendly, Short, Detailed).
  * Strict cultural rule: Never mention cash amounts in messages even if known.
  * Delivery tracking (Sent via WhatsApp, SMS, Printed Card, In Person) and status audit history.
* **Gift History & Reciprocity Ledger (`frontend/gift-history.html` & `services/history_service.py`):**
  * 2-column comparative ledger: Gifts received at Farhana's wedding vs gifts given in return at future weddings.
  * Return gift recorder preventing guesswork or speculative market evaluations.
* **Analytics & Quality Assurance:**
  * Reports & CSV export engine (`services/report_service.py`, `frontend/reports.html`).
  * Realistic database seed script (`scripts/seed_data.py`).
  * Automated Pytest test suite (`test_ai_processing.py`, `test_thank_you.py`, `test_history_reciprocity.py`, `test_reports.py`).

---

### 🤝 Integration & Collaboration Protocol
1. **API Contracts:** Defined in `app/schemas/` using Pydantic models.
2. **Database Migrations:** Managed centrally via Alembic.
3. **Continuous Verification:** Pytest passes 15/15 unit and integration tests.
