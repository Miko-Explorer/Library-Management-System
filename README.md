# LibSys — Library Management System

- A Streamlit + MySQL app for managing books, members, loans, fines, and staff in a library setting.
- Features a dark glassmorphism UI with full CRUD across all schema tables and automatic overdue fine calculation.

---

## Table of Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Quick start](#quick-start)
- [Database setup](#database-setup)
- [Database schema](#database-schema)
- [Application modules](#application-modules)
- [UI / UX](#ui--ux)
- [Security](#security)
- [Development & testing](#development--testing)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

- **Dashboard** — real-time system statistics (total books, members, active loans, unpaid fines); 4 interactive Plotly charts (genre bar, member status donut, loans-over-time spline, fine histogram); recent loan activity feed
- **Books management** — full CRUD; genre dropdown (10 genres); duplicate title prevention; delete blocked if book has associated loans or fines
- **Members management** — full CRUD; email and phone regex validation; duplicate detection (email, phone); delete blocked if member has associated loans or fines
- **Loans management** — full CRUD; issue new loans (auto due date = loan date + 7 days); return book with overdue fine auto-calculation (₱5/day); available books filter (excludes currently loaned)
- **Fines management** — full CRUD; view with paid/unpaid totals; manual fine issue (Lost / Damaged / Overdue); auto-fine on overdue book return
- **Staff management** — full CRUD; email, phone, and duplicate validation (name, username, email, phone); no foreign-key dependency checks on delete

---

## Tech stack

| Component | Technology |
|---|---|
| Language | Python 3.8+ |
| Web framework | Streamlit 1.23+ |
| Data manipulation | pandas 1.5+ |
| DB connector | mysql-connector-python 8.0+ |
| Charts | Plotly 5.0+ |
| Database server | MySQL 8.0+ |
| UI styling | Custom CSS (glassmorphism dark theme) |

See `requirements.txt` for pinned versions.

---

## Project structure

```
Library-Management-System/
├─ .gitignore                           # Ignores secrets, cache, venvs, IDE files
├─ .streamlit/
│  └─ secrets.toml                      # MySQL credentials (git-ignored)
├─ Database & ERD/
│  ├─ ERD_library_db.mwb                # MySQL Workbench model
│  ├─ ERD_library_db.pdf                # ERD diagram (PDF)
│  ├─ library_sys_management (updated).sql  # DB + tables DDL
│  └─ sample_library_entries.sql        # 50+ sample records per table
├─ books.py                             # Book CRUD
├─ dashboard.py                         # Dashboard metrics + charts
├─ database.py                          # Connection + query helpers
├─ fines.py                             # Fine management
├─ loans.py                             # Loan lifecycle
├─ main.py                              # App entry, CSS theme, routing
├─ members.py                           # Member CRUD
├─ README.md                            # This file
├─ requirements.txt                     # Python dependencies
└─ staff.py                             # Staff CRUD
```

---

## Quick start

- **Clone the repo:**
  ```bash
  git clone https://github.com/Miko-Explorer/MySQL-Based-Projects.git
  cd "MySQL-Based-Projects/Library Management System"
  ```

- **Set up a virtual environment and install deps:**
  ```bash
  python -m venv .venv
  source .venv/bin/activate            # Linux/macOS
  .venv\Scripts\activate               # Windows
  pip install -r requirements.txt
  ```

- **Configure `.streamlit/secrets.toml`** with MySQL credentials:
  ```toml
  [mysql]
  host = "localhost"
  port = 3306
  user = "root"
  password = "your_mysql_password"
  database = "library_db"
  ```
  > Never commit this file — it's in `.gitignore`.

- **Run database scripts** (see [Database setup](#database-setup)).

- **Launch the app:**
  ```bash
  streamlit run main.py
  ```
  Open `http://localhost:8501`.

---

## Database setup

- Scripts live in `Database & ERD/`.
- **Run in order:**

  1. **Create database and tables:**
     ```bash
     mysql -u root -p < "Database & ERD/library_sys_management (updated).sql"
     ```
     Creates `library_db`, all 5 tables (`books`, `members`, `loans`, `fines`, `staff`) with FKs and CHECK/ENUM constraints.

  2. **(Optional) Insert sample data:**
     ```bash
     mysql -u root -p library_db < "Database & ERD/sample_library_entries.sql"
     ```
     Adds 50+ entries per table (books, members, loans, fines, staff) for testing.

- Alternatively, execute the SQL files in MySQL Workbench or any MySQL client.
- On first app launch, `database.py:init_db()` also auto-creates tables if they don't exist.

---

## Database schema

### `books` table

| Column | Type | Constraints |
|---|---|---|
| `book_id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` |
| `book_title` | `VARCHAR(500)` | `NOT NULL`, `UNIQUE` |
| `book_genre` | `ENUM('Action Adventure','Classics','Fantasy','Graphic Novels','Historical Fiction','Horror','Mystery','Romance','Sci-Fi','Suspense/Thriller')` | `NOT NULL` |
| `year_published` | `YEAR` | `NOT NULL` |

### `members` table

| Column | Type | Constraints |
|---|---|---|
| `member_id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` (starts 100) |
| `full_name` | `VARCHAR(100)` | `NOT NULL` |
| `email` | `VARCHAR(100)` | `NOT NULL`, `UNIQUE` |
| `phone` | `VARCHAR(11)` | `NOT NULL`, `UNIQUE` |
| `address` | `VARCHAR(100)` | `NOT NULL` |
| `membership_date` | `DATETIME` | `NOT NULL` |
| `is_active` | `ENUM('Active','Inactive')` | `NOT NULL` |

### `loans` table

| Column | Type | Constraints |
|---|---|---|
| `loan_id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` (starts 200) |
| `book_id` | `INT` | `NOT NULL`, `FK → books(book_id)` |
| `member_id` | `INT` | `NOT NULL`, `FK → members(member_id)` |
| `loan_date` | `DATETIME` | `NOT NULL` |
| `due_date` | `DATETIME` | `NOT NULL` |
| `return_date` | `DATETIME` | `NULL` (NULL = active / not yet returned) |

### `fines` table

| Column | Type | Constraints |
|---|---|---|
| `fine_id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` (starts 300) |
| `book_id` | `INT` | `NOT NULL`, `FK → books(book_id)` |
| `member_id` | `INT` | `NOT NULL`, `FK → members(member_id)` |
| `amount` | `DECIMAL(10,2)` | `DEFAULT 0.00` |
| `reason` | `ENUM('Lost','Damaged','Overdue')` | `NOT NULL` |
| `issued_date` | `DATETIME` | `NOT NULL` |
| `paid` | `DECIMAL(10,2)` | `DEFAULT 0.00` |
| `paid_date` | `DATETIME` | `NULL` (NULL = unpaid) |

### `staff` table

| Column | Type | Constraints |
|---|---|---|
| `staff_id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` |
| `full_name` | `VARCHAR(100)` | `NOT NULL` |
| `username` | `VARCHAR(100)` | `NOT NULL`, `UNIQUE` |
| `email` | `VARCHAR(100)` | `NOT NULL`, `UNIQUE` |
| `phone` | `VARCHAR(11)` | `NOT NULL`, `UNIQUE` |
| `address` | `VARCHAR(100)` | `NOT NULL` |
| `roles` | `ENUM('Admin','Librarian','Asst. Librarian')` | |
| `hire_date` | `DATE` | `NOT NULL` |
| `last_login` | `DATETIME` | `NOT NULL` |
| `is_active` | `ENUM('Active','Inactive')` | `NOT NULL` |

---

## Application modules

| Module | File | Role |
|---|---|---|
| **Entry point** | `main.py` | Page config, glassmorphism CSS, sidebar radio nav, page routing to 6 modules |
| **Database layer** | `database.py` | `get_connection()` + `query()` helpers; `init_db()` auto-creates tables |
| **Dashboard** | `dashboard.py` | `show()` — key metrics, 4 Plotly charts, recent loan activity table |
| **Books management** | `books.py` | `show()` — full CRUD with genre/year filtering and FK dependency checks |
| **Members management** | `members.py` | `show()` — full CRUD with email/phone validation and FK dependency checks |
| **Loans management** | `loans.py` | `show()` — full CRUD with auto due-date, return processing, and fine calculation |
| **Fines management** | `fines.py` | `show()` — full CRUD with paid/unpaid totals and manual fine issue |
| **Staff management** | `staff.py` | `show()` — full CRUD with email/phone validation |

### "Cannot delete this book/member because it has associated loans or fines"
- Delete or resolve the related loans/fines first

### Tables not created automatically
- Does the MySQL user have `CREATE DATABASE` / `CREATE TABLE` privileges?
- Check the terminal for error output on launch

### Changes not showing after CRUD
- All operations call `st.rerun()` automatically. If data seems stale, re-click the sidebar page or refresh the browser.

---

## Author

**Enrico Miguel Veloso** — enrico.veloso1605@gmail.com

---

*Library Management System v2.0 — Built with Streamlit & MySQL*