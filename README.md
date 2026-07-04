# Library Management System

A modular library management system built with **Streamlit** and **MySQL** — full CRUD operations, automatic overdue fine calculation, and interactive Plotly dashboards in a glass‑morphism dark UI.

---

## Table of Contents

- [Features](#features)
- [Navigation Overview](#navigation-overview)
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
- Live key metrics: Total Books, Total Members (with active count), Active Loans, Unpaid Fines
- **Books by Genre** — interactive bar chart (Plotly)
- **Member Status** — donut pie chart (Active vs Inactive)
- **Loans Over Time** — spline line chart grouped by month
- **Fine Amount Distribution** — histogram of fine amounts
- **Recent Loan Activity** — scrollable table of the 5 most recent loans with book and member names

### Books Management
- **View Books** — full table of all books with ID, title, genre, and publication year
- **Add Book** — form with title, genre dropdown (10 genres), and year picker; duplicate title prevention
- **Update Book** — select a book, edit title/genre/year inline
- **Delete Book** — safety check prevents deletion if the book has associated loans or fines

### Members Management
- **View Members** — table of all members with contact info, registration date, and status
- **Register Member** — form with name, email (regex validated), 11-digit phone (regex validated), address, and active/inactive status; duplicate detection
- **Update Member** — edit all fields inline; validation re-applied
- **Delete Member** — safety check prevents deletion if the member has associated loans or fines

### Loans Management
- **View Loans** — table joining loans with book titles and member names, showing loan/return dates and status (Active/Returned)
- **New Loan** — select from available books (not currently loaned) and active members; auto-sets due date 7 days from loan date
- **Return Book** — select an active loan, choose return date; automatically calculates overdue fines (₱5/day) and records them in the fines table

### Fines Management
- **View Fines** — table with book, member, amount, reason, issued date, paid amount, and status (Paid/Unpaid); summary metrics for total unpaid and total paid
- **Issue Fine** — manually create a fine for Lost/Damaged/Overdue reasons, selecting book and member

### Staff Management
- **View Staff** — table of all staff with username, contact info, role, hire date, and status
- **Add Staff** — form with validation for email format and 11-digit phone; duplicate detection for name, username, email, and phone
- **Update Staff** — edit all fields inline with validation
- **Delete Staff** — direct deletion (no dependency checks)

### UI / UX
- **Glass-morphism Theme** — dark gradient background, blurred glass cards, custom scrollbar, professional typography (Inter font)
- **Toast Notifications** — fading success/error toasts on every CRUD operation
- **Tab-based Navigation** — each page uses tabs to separate view/add/update/delete workflows
- **Sidebar Status** — database connection indicator and system version

---

## Navigation Overview

The sidebar provides 6 navigation pages:

| Page       | Iconless Label | Tabs Inside                              |
|------------|----------------|------------------------------------------|
| Dashboard  | Dashboard      | Metrics + 4 charts + recent activity     |
| Books      | Books          | View Books / Add Book / Update & Delete  |
| Members    | Members        | View Members / Add Member / Update & Delete |
| Loans      | Loans          | View Loans / New Loan / Return Book      |
| Fines      | Fines          | View Fines / Issue Fine                  |
| Staff      | Staff          | View Staff / Add Staff / Update & Delete |

---

## Database Schema

The schema is auto-created on first run by `database.py:init_db()`. Five tables:

### `books`
| Column         | Type          | Constraints              |
|----------------|---------------|--------------------------|
| book_id        | INT           | PK, AUTO_INCREMENT        |
| book_title     | VARCHAR(500)  | NOT NULL, UNIQUE          |
| book_genre     | ENUM(10 vals) | NOT NULL                  |
| year_published | YEAR          | NOT NULL                  |

### `members`
| Column          | Type           | Constraints              |
|-----------------|----------------|--------------------------|
| member_id       | INT            | PK, AUTO_INCREMENT (100) |
| full_name       | VARCHAR(100)   | NOT NULL                 |
| email           | VARCHAR(100)   | NOT NULL, UNIQUE          |
| phone           | VARCHAR(11)    | NOT NULL, UNIQUE          |
| address         | VARCHAR(100)   | NOT NULL                 |
| membership_date | DATETIME       | NOT NULL                 |
| is_active       | ENUM(Active/Inactive) | NOT NULL          |

### `loans`
| Column      | Type     | Constraints                    |
|-------------|----------|--------------------------------|
| loan_id     | INT      | PK, AUTO_INCREMENT (200)       |
| book_id     | INT      | NOT NULL, FK → books           |
| member_id   | INT      | NOT NULL, FK → members         |
| loan_date   | DATETIME | NOT NULL                       |
| due_date    | DATETIME | NOT NULL                       |
| return_date | DATETIME | NULL (NULL = not yet returned) |

### `fines`
| Column     | Type           | Constraints                    |
|------------|----------------|--------------------------------|
| fine_id    | INT            | PK, AUTO_INCREMENT (300)       |
| book_id    | INT            | NOT NULL, FK → books           |
| member_id  | INT            | NOT NULL, FK → members         |
| amount     | DECIMAL(10,2)  | DEFAULT 0.00                   |
| reason     | ENUM(3 vals)   | NOT NULL (Lost/Damaged/Overdue)|
| issued_date| DATETIME       | NOT NULL                       |
| paid       | DECIMAL(10,2)  | DEFAULT 0.00                   |
| paid_date  | DATETIME       | NULL (NULL = unpaid)           |

### `staff`
| Column     | Type                | Constraints              |
|------------|---------------------|--------------------------|
| staff_id   | INT                 | PK, AUTO_INCREMENT       |
| full_name  | VARCHAR(100)        | NOT NULL                 |
| username   | VARCHAR(100)        | NOT NULL, UNIQUE          |
| email      | VARCHAR(100)        | NOT NULL, UNIQUE          |
| phone      | VARCHAR(11)         | NOT NULL, UNIQUE          |
| address    | VARCHAR(100)        | NOT NULL                 |
| roles      | ENUM(3 vals)        | NULLable                  |
| hire_date  | DATE                | NOT NULL                 |
| last_login | DATETIME            | NOT NULL                 |
| is_active  | ENUM(Active/Inactive)| NOT NULL                 |

> Reference DDL: `Database & ERD/library_sys_management (updated).sql`

---

## Project Structure

```
Library-Management-System/
├── .gitignore
├── .streamlit/
│   └── secrets.toml
├── Database & ERD/
│   ├── ERD_library_db.mwb
│   ├── ERD_library_db.pdf
│   └── library_sys_management (updated).sql
├── books.py
├── dashboard.py
├── database.py
├── fines.py
├── loans.py
├── main.py
├── members.py
├── README.md
├── requirements.txt
└── staff.py
```

---

## Module Architecture

The application follows a modular single-page architecture:

```
main.py (entry point)
├── st.set_page_config()
├── Custom CSS injection (glassmorphism theme)
├── database.init_db()            # Auto-create tables
├── Sidebar navigation (radio buttons)
├── Routing to page modules
│   ├── dashboard.show()          # Metrics + charts
│   ├── books.show()              # Book CRUD
│   ├── members.show()            # Member CRUD
│   ├── loans.show()              # Loan management
│   ├── fines.show()              # Fine management
│   └── staff.show()              # Staff CRUD
└── Footer
```

Each page module in `books.py`, `members.py`, `loans.py`, `fines.py`, `staff.py`, and `dashboard.py` exports a single `show()` function that renders its entire page content using Streamlit elements. `database.py` serves as the sole data access layer — all database connections, queries, and mutations go through it.

### Function Reference — `database.py`

| Function              | Purpose                                          |
|-----------------------|--------------------------------------------------|
| `get_connection()`    | Returns a MySQL connection or stops the app      |
| `init_db()`           | Creates database and all 5 tables if missing     |
| `execute_query()`     | Generic query executor (fetch or commit)         |
| `get_table_data()`    | SELECT wrapper with optional WHERE clause        |
| `get_books()`         | Fetch all books                                  |
| `get_members()`       | Fetch all members                                |
| `get_loans()`         | Fetch all loans                                  |
| `get_fines()`         | Fetch all fines                                  |
| `get_staff()`         | Fetch all staff                                  |
| `has_related_records()`| Check foreign-key dependencies before deletion  |
| `calculate_fine()`    | Compute overdue fine for a loan                  |
| `create_fine()`       | INSERT a new fine record                         |
| `update_loan_return()`| Set return date, auto-create overdue fine if due |

---

## Getting Started

### Prerequisites

- **Python 3.8+** installed on your system
- **MySQL Server** running (local or remote)
- **pip** package manager

### Installation

1. **Clone the repository**
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

4. **Configure database credentials**

   Edit `database.py` and update the `DB_CONFIG` dictionary:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_mysql_password',
       'database': 'library_db',
       'port': 3306
   }
   ```

   Alternatively, configure `.streamlit/secrets.toml`:
   ```toml
   [mysql]
   host = "localhost"
   port = 3306
   user = "root"
   password = "your_mysql_password"
   database = "library_db"
   ```

5. **Run the application**
   ```bash
   streamlit run main.py
   ```

6. **Open your browser** and navigate to **http://localhost:8501**

   > The database tables are created automatically on first launch.

---

## Usage Guide

### First-time setup
1. Launch the app — tables are created automatically.
2. Go to **Books** > **Add Book** and add several books across different genres.
3. Go to **Members** > **Add Member** and register at least one active member.
4. Go to **Loans** > **New Loan** and issue a loan by selecting a book and member.
5. Go to **Loans** > **Return Book** to process a return (try a date past due to see fines).

### Daily operations workflow
- **Adding books:** Books > Add Book tab
- **Registering members:** Members > Add Member tab
- **Issuing loans:** Loans > New Loan tab
- **Processing returns:** Loans > Return Book tab (fines auto-calculated)
- **Viewing overdue books:** Not a separate page — filter via the Loans table (look for "Active" status with past due dates)
- **Managing fines:** Fines > View Fines / Issue Fine tabs
- **Managing staff:** Staff > Add Staff / Update & Delete tabs

---

## Fine Calculation Logic

The system uses two fine mechanisms:

### Automatic (on book return)
- Triggered when **Loans > Return Book** is processed
- Calculated as: `days_overdue × ₱5.00`
- A new record is inserted into the `fines` table with reason `"Overdue"`
- Paid status starts at `0.00` (unpaid)

### Manual (via Fines tab)
- Navigate to **Fines > Issue Fine**
- Select book, member, reason (Lost/Damaged/Overdue), and amount
- Useful for lost books, physical damage, or retroactive fines

### Adjusting the fine rate
Edit the rate in `database.py`:
```python
fine_amount = days_overdue * 5   # Change 5 to your desired daily rate
```

### Adjusting lost/damaged book price
Edit in `database.py`:
```python
DEFAULT_BOOK_PRICE = 500.00      # Default value for lost/damaged calculations
```

---

## Technologies

| Layer       | Technology                          |
|-------------|-------------------------------------|
| **UI**      | Streamlit 1.23+                     |
| **Charts**  | Plotly Express, Plotly Graph Objects |
| **Data**    | Pandas                              |
| **Database**| MySQL (via mysql-connector-python)  |
| **Styling** | Custom CSS (glassmorphism, Inter font, dark theme) |
| **Language**| Python 3.8+                         |

---

## Troubleshooting

### "Database connection failed"
- Ensure MySQL Server is running
- Verify credentials in `DB_CONFIG` inside `database.py`
- Check that the MySQL port (default 3306) is open and not firewalled
- For remote hosts, ensure MySQL user has remote access privileges

### "No module named 'streamlit'"
- Dependencies are not installed. Run:
  ```bash
  pip install -r requirements.txt
  ```

### "A book with this title already exists"
- The `book_title` column has a UNIQUE constraint. Titles must be unique.

### "Cannot delete this book because it has associated loans or fines"
- The book has records in the `loans` or `fines` tables. Delete those first, or mark them as returned/paid.

### Tables not created automatically
- Ensure the MySQL user has `CREATE DATABASE` and `CREATE TABLE` privileges
- Check the terminal for error output when the app starts

### Changes not showing after CRUD
- All CRUD operations call `st.rerun()` automatically. If data seems stale, click the sidebar page again or refresh the browser.

---

## Author

**Enrico Miguel Veloso**  
enrico.veloso1605@gmail.com

---

*Library Management System v2.0 — Built with Streamlit & MySQL*
