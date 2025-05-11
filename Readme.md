# Grant Budget Generator (Budget Buddy)

**Grant Budget Generator** (a.k.a. **Budget Buddy**) is a web‑based application designed to streamline the creation, management, and export of multi‑year research grant budgets, fully compliant with NSF and NIH guidelines.

---

## Table of Contents

- [Grant Budget Generator (Budget Buddy)](#grant-budget-generator-budget-buddy)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Key Features](#key-features)
  - [System Architecture](#system-architecture)
  - [Data Model \& ER Diagram](#data-model--er-diagram)
  - [Setup \& Installation](#setup--installation)
    - [Prerequisites](#prerequisites)
    - [Cloning the Repository](#cloning-the-repository)
    - [Environment Configuration](#environment-configuration)
    - [Virtual Environment \& Dependencies](#virtual-environment--dependencies)
  - [Database Initialization \& Seeding](#database-initialization--seeding)
    - [Schema Migration](#schema-migration)
    - [Data Migration (MySQL → Postgres)](#data-migration-mysql--postgres)
    - [Resetting Data](#resetting-data)
  - [Running the Application](#running-the-application)
    - [Development Mode](#development-mode)
    - [Production Mode (Gunicorn)](#production-mode-gunicorn)
  - [Deployment to Render](#deployment-to-render)
  - [Code Structure](#code-structure)
  - [Usage Workflow](#usage-workflow)
  - [API Endpoints \& Dash Pages](#api-endpoints--dash-pages)
  - [Troubleshooting](#troubleshooting)
  - [Contributing](#contributing)
  - [License](#license)

---

## Overview

The Grant Budget Generator helps researchers:

* Define roles (PI, Co-PI, staff, students) with annual rate increases and fringe benefits.
* Categorize expenses (equipment, travel, materials, participant support).
* Build detailed year‑by‑year budgets.
* Validate compliance with funder rules (NSF, NIH).
* Export budgets to Excel for proposal submission.

By combining Flask for user management and Dash for interactive dashboards, the application offers both secure flows (login/register) and dynamic analytics.

---

## Key Features

* **Authentication**: Secure registration, login, session management (Flask-Login & Bcrypt).
* **Role-based Rates**: Define base rates and year-over-year increases for multiple personnel categories.
* **Fringe Benefits**: Manage general, NSF-specific, and NIH-specific fringe rates.
* **Expense Tracking**: Create categories & subcategories with descriptions.
* **Grant CRUD**: Create, read, update, delete grants with metadata (title, agency, duration, dates, status).
* **Personnel & Travel Planning**: Itemize personnel assignments and travel entries.
* **Interactive Dashboards**: Dash pages for dashboard, generate grants, subawards, settings, profile.
* **Excel Export**: Download generated budgets in multiple templates.
* **Admin Interface**: Secure pages for data maintenance (roles, fringe rates, categories).

---

## System Architecture

```
[User Browser] ↔ Flask (Jinja2 templates for login/register)
                          ↔ Dash (Single‑page app under /home)
                          ↔ SQLAlchemy ORM ↔ PostgreSQL
```

* **Flask** handles authentication, templating, and serves the Dash app.
* **Dash** (Plotly) builds interactive UI under `/home`.
* **SQLAlchemy** abstracts database operations on PostgreSQL.
* **Gunicorn** serves the app in production.

---

## Data Model & ER Diagram

Entities include:

* **Users** (id, username, first\_name, last\_name, email, password, timestamps)
* **Personnel Compensation** (NSF & NIH tables: role + year‑rate increases)
* **Fringe Rates** (general, NSF, NIH: role, year, rate)
* **Expense Categories & Subcategories**
* **Grants** (linked to Users, with metadata)
* **Grant Personnel**, **Grant Travel**, **Grant Materials**
* **Personnel Tables**: PI, Co‑PI, Staff, Postdoc, GRA, Temp Help, Undergrad
* **Travel Itineraries**, **Graduate Student Costs**

*(See `docs/er-diagram.png` for the visual diagram.)*

---

## Setup & Installation

### Prerequisites

* Python 3.10+
* PostgreSQL instance (local or Render managed)
* (Optional) MySQL if migrating legacy data

### Cloning the Repository

```bash
git clone https://github.com/your-org/grant-budget-generator.git
cd grant-budget-generator
```

### Environment Configuration

Create a copy of our example environment file:

```bash
cp .env.example .env
# Edit .env with your own secrets & URLs
```

Your `.env` should include:

```dotenv
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
APP_SECRET_KEY="<your-secret-key>"
ADMIN_SECRET="<admin-secret>"
POSTGRES_DATABASE_URL="postgresql+psycopg2://<user>:<pw>@<host>:5432/<db>?sslmode=require"
MYSQL_DATABASE_URL="mysql+pymysql://<user>:<pw>@<host>:3306/<db>"
```

### Virtual Environment & Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Database Initialization & Seeding

### Schema Migration

Recreate tables in Postgres:

```bash
python migrate_schema.py
```

### Data Migration (MySQL → Postgres)

If migrating existing MySQL data:

```bash
python data_migrate.py
```

### Resetting Data

To **wipe rows** but keep schema:

```sql
TRUNCATE TABLE table1, table2, ... RESTART IDENTITY CASCADE;
```

To **drop all** objects:

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

---

## Running the Application

### Development Mode

```bash
flask --app app.py --debug run
# Access at http://127.0.0.1:5000
```

### Production Mode (Gunicorn)

```bash
gunicorn app:app --bind 0.0.0.0:8000 --workers 4
```

---

## Deployment to Render

1. Connect your GitHub repo to Render.
2. In **Build Command**, enter:

   ```bash
   pip install -r requirements.txt
   ```
3. In **Start Command**, enter:

   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
4. Set the following **Environment Variables** in Render:

   * `APP_SECRET_KEY`
   * `ADMIN_SECRET`
   * `POSTGRES_DATABASE_URL`
5. Deploy—Render will build & start Gunicorn automatically.

---

## Code Structure

```
├── app.py             # Flask + Dash entrypoint
├── models.py          # SQLAlchemy models & DB initialization
├── pages/             # dash-registered page modules
├── migrate_schema.py  # DDL-only migration script
├── data_migrate.py    # Full data migration MySQL→Postgres
├── requirements.txt   # pip dependencies
├── .env.example       # sample environment variables
├── static/            # CSS, JS, images
├── templates/         # Jinja2 templates (login, register)
└── README.md          # this documentation
```

---

## Usage Workflow

1. **Register** at `/register` → confirm your account.
2. **Login** at `/login` → redirected to `/home/dashboard`.
3. **Dashboard** page: overview charts & grant list.
4. **Generate Grants**: step‑by‑step budget creation wizard.
5. **Subawards**: manage subaward budgets.
6. **Settings/Profile**: theme toggle, view personal analytics.
7. **Logout**: end your session securely.

---

## API Endpoints & Dash Pages

* `GET /` → login page
* `GET/POST /login`, `/register`
* Dash app mounted at `/home/*` via `Dash(..., server=app)`

  * `/home/dashboard` → Dashboard page module
  * `/home/generate-grants` → Grant generator wizard
  * `/home/subawards`, `/home/settings`, `/home/profile`

---

## Troubleshooting

* **`ModuleNotFoundError: reportlab`** → `pip install reportlab`
* **SSL errors** → ensure `?sslmode=require` on Postgres URL
* **MultipleResultsFound** → dedupe database or use `first()`/aggregates
* **Dash deprecation** → change `import dash_table` → `from dash import dash_table`

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Commit & push changes
4. Open a Pull Request for review

---

## License

Licensed under MIT. See `LICENSE` for details.
