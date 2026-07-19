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

---

## Technologies

| Layer       | Technology                              |
|-------------|----------------------------------------|
| **UI**      | Streamlit 1.23+                        |
| **Charts**  | Plotly Express, Plotly Graph Objects   |
| **Data**    | Pandas                                 |
| **Database**| MySQL (mysql-connector-python)         |
| **Styling** | Custom CSS (glassmorphism, dark theme) |
| **Language**| Python 3.8+                            |

---

## Troubleshooting

### "Database connection failed"
- Is MySQL Server running?
- Check credentials in `.streamlit/secrets.toml`
- Is port 3306 open and not firewalled?
- For remote hosts, does the MySQL user have remote access?

### "No module named 'streamlit'"
- Dependencies not installed:
  ```bash
  pip install -r requirements.txt
  ```

### "A book with this title already exists"
- `book_title` has a UNIQUE constraint — titles must be unique

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