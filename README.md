# LibSys — Library Management System

- A Streamlit + MySQL app for managing books, members, loans, fines, and staff in a library setting.
- Features a dark glassmorphism UI with full CRUD across all schema tables and automatic overdue fine calculation.

---

## Table of Contents

- [Features](#features)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Module Architecture](#module-architecture)
- [Getting Started](#getting-started)
- [Usage Guide](#usage-guide)
- [Fine Calculation Logic](#fine-calculation-logic)
- [Technologies](#technologies)
- [Troubleshooting](#troubleshooting)
- [Author](#author)

---

## Features

### Dashboard
- Live metrics: Total Books, Total Members (active count), Active Loans, Unpaid Fines
- **Books by Genre** — interactive Plotly bar chart
- **Member Status** — donut pie chart (Active vs Inactive)
- **Loans Over Time** — spline chart grouped by month
- **Fine Amount Distribution** — histogram
- **Recent Loan Activity** — scrollable table of the 5 latest loans

### Books Management
- View / Add / Update / Delete books
- Genre dropdown (10 genres) + year picker
- Duplicate title prevention via UNIQUE constraint
- Delete blocked if book has associated loans or fines

### Members Management
- View / Register / Update / Delete members
- Email and phone regex validation
- Duplicate detection for email and phone
- Delete blocked if member has associated loans or fines

### Loans Management
- View all loans (joins book title + member name, status: Active / Returned)
- Issue new loan — pick from available books (not currently loaned) and active members; due date auto-set to loan date + 7 days
- Return book — select active loan, pick return date; overdue fine (₱5/day) auto-calculated and recorded

### Fines Management
- View fines table with paid/unpaid status + summary totals
- Manually issue fines (Lost / Damaged / Overdue)

### Staff Management
- View / Add / Update / Delete staff
- Validation: email format, 11-digit phone, duplicate checks on name/username/email/phone
- No foreign-key dependency checks on delete

### UI / UX
- Glass-morphism theme: dark gradient, blurred cards, custom scrollbar, Inter font
- Toast notifications on every CRUD operation
- Tab-based navigation per page (view / add / update / delete)
- Sidebar with 6 pages + database status indicator

---

## Database Schema

Auto-created on first run by `database.py:init_db()`. Five tables:

| Table     | Key Columns                                      |
|-----------|--------------------------------------------------|
| `books`   | `book_id` (PK), `book_title` (UNIQUE), `book_genre` (ENUM, 10 values), `year_published` |
| `members` | `member_id` (PK, starts 100), `email` (UNIQUE), `phone` (UNIQUE), `is_active` |
| `loans`   | `loan_id` (PK, starts 200), `book_id` (FK), `member_id` (FK), `loan_date`, `due_date`, `return_date` (NULL = active) |
| `fines`   | `fine_id` (PK, starts 300), `book_id` (FK), `member_id` (FK), `amount`, `reason` (Lost/Damaged/Overdue), `paid`, `paid_date` |
| `staff`   | `staff_id` (PK), `username` (UNIQUE), `email` (UNIQUE), `phone` (UNIQUE), `roles`, `hire_date`, `is_active` |

- Reference DDL: `Database & ERD/library_sys_management (updated).sql`

---

## Project Structure

```
Library-Management-System/
├── .gitignore
├── .streamlit/
│   └── secrets.toml               # MySQL credentials
├── Database & ERD/
│   ├── ERD_library_db.mwb
│   ├── ERD_library_db.pdf
│   └── library_sys_management (updated).sql
├── books.py                       # Book CRUD
├── dashboard.py                   # Metrics + charts
├── database.py                    # Data access layer
├── fines.py                       # Fine management
├── loans.py                       # Loan lifecycle
├── main.py                        # Entry point, routing
├── members.py                     # Member CRUD
├── README.md
├── requirements.txt
└── staff.py                       # Staff CRUD
```

---

## Module Architecture

- **`main.py`** — entry point: page config, CSS injection, sidebar nav, routing
- **`database.py`** — sole data access layer (all DB calls go through it)
- **`books.py`**, **`members.py`**, **`loans.py`**, **`fines.py`**, **`staff.py`** — each exports a single `show()` function for its page
- **`dashboard.py`** — exports `show()` with metrics + 4 Plotly charts + recent activity

### `database.py` Function Reference

| Function                | Purpose                                          |
|-------------------------|--------------------------------------------------|
| `get_connection()`      | Returns a MySQL connection from `st.secrets["mysql"]` |
| `query()`               | Generic query executor (fetch rows or commit)    |
| `init_db()`             | Creates database + all 5 tables if missing       |
| `get_books()`           | Fetch all books                                  |
| `get_members()`         | Fetch all members                                |
| `get_loans()`           | Fetch all loans                                  |
| `get_fines()`           | Fetch all fines                                  |
| `get_staff()`           | Fetch all staff                                  |
| `has_related_records()` | Check FK dependencies before delete              |
| `calculate_fine()`      | Compute overdue fine for a loan                  |
| `create_fine()`         | INSERT a new fine record                         |
| `update_loan_return()`  | Set return date, auto-create overdue fine if due |

---

## Getting Started

### Prerequisites
- **Python 3.8+**
- **MySQL Server** (local or remote)
- **pip** package manager

### Installation

1. **Clone the repo**
   ```bash
   git clone <repository-url>
   cd Library-Management-System
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MySQL credentials** in `.streamlit/secrets.toml`
   ```toml
   [mysql]
   host = "localhost"
   port = 3306
   user = "root"
   password = "your_mysql_password"
   database = "library_db"
   ```

5. **Run the app**
   ```bash
   streamlit run main.py
   ```

6. **Open** http://localhost:8501 in your browser
   - Tables are created automatically on first launch

---

## Usage Guide

### First-time setup
1. Launch the app — tables auto-create
2. **Books > Add Book** — add several books across different genres
3. **Members > Add Member** — register at least one active member
4. **Loans > New Loan** — issue a loan by selecting a book and member
5. **Loans > Return Book** — process a return (try a past-due date to see fines)

### Daily operations
- **Add books** → Books > Add Book tab
- **Register members** → Members > Add Member tab
- **Issue loans** → Loans > New Loan tab
- **Process returns** → Loans > Return Book tab (fines auto-calculated)
- **View overdue books** → Loans table; look for "Active" status with past due dates
- **Manage fines** → Fines > View Fines / Issue Fine tabs
- **Manage staff** → Staff > Add Staff / Update & Delete tabs

---

## Fine Calculation Logic

### Automatic (on book return)
- Triggered by **Loans > Return Book**
- Formula: `days_overdue × ₱5.00`
- Inserts a `fines` row with reason `"Overdue"` and `paid = 0.00`
- Adjust daily rate in `database.py`:
  ```python
  fine_amount = days_overdue * 5   # Change 5 to your desired rate
  ```

### Manual (via Fines tab)
- Navigate to **Fines > Issue Fine**
- Select book, member, reason (Lost/Damaged/Overdue), and amount
- Used for lost books, physical damage, or retroactive fines
- Adjust default book price in `database.py`:
  ```python
  DEFAULT_BOOK_PRICE = 500.00
  ```

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