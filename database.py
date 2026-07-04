import mysql.connector
from mysql.connector import Error
import streamlit as st
from datetime import datetime, timedelta

DEFAULT_BOOK_PRICE = 500.00

def get_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"].get("port", 3306)
        )
    except KeyError as e:
        st.error(f"Missing MySQL configuration in secrets.toml: {e}")
        return None
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None

def query(sql, params=None, fetch=True):
    conn = get_connection()
    if not conn:
        return [] if fetch else None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            result = cur.fetchall()
        else:
            conn.commit()
            result = cur.lastrowid
        cur.close()
        conn.close()
        return result
    except Error as e:
        st.error(f"Query error: {e}")
        if not fetch:
            conn.rollback()
        cur.close()
        conn.close()
        return [] if fetch else None

def init_db():
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS library_db")
    cursor.execute("USE library_db")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INT AUTO_INCREMENT PRIMARY KEY,
            book_title VARCHAR(500) NOT NULL UNIQUE,
            book_genre ENUM('Action Adventure', 'Classics', 'Fantasy',
                'Graphic Novels', 'Historical Fiction', 'Horror',
                'Mystery', 'Romance', 'Sci-Fi', 'Suspense/Thriller') NOT NULL,
            year_published YEAR NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            phone VARCHAR(11) NOT NULL UNIQUE,
            address VARCHAR(100) NOT NULL,
            membership_date DATETIME NOT NULL,
            is_active ENUM('Active', 'Inactive') NOT NULL
        ) AUTO_INCREMENT = 100
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT NOT NULL,
            member_id INT NOT NULL,
            loan_date DATETIME NOT NULL,
            due_date DATETIME NOT NULL,
            return_date DATETIME NULL,
            FOREIGN KEY (book_id) REFERENCES books(book_id),
            FOREIGN KEY (member_id) REFERENCES members(member_id)
        ) AUTO_INCREMENT = 200
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fines (
            fine_id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT NOT NULL,
            member_id INT NOT NULL,
            amount DECIMAL(10,2) DEFAULT 0.00,
            reason ENUM('Lost', 'Damaged', 'Overdue') NOT NULL,
            issued_date DATETIME NOT NULL,
            paid DECIMAL(10,2) DEFAULT 0.00,
            paid_date DATETIME NULL,
            FOREIGN KEY (book_id) REFERENCES books(book_id),
            FOREIGN KEY (member_id) REFERENCES members(member_id)
        ) AUTO_INCREMENT = 300
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            phone VARCHAR(11) NOT NULL UNIQUE,
            address VARCHAR(100) NOT NULL,
            roles ENUM('Admin', 'Librarian', 'Asst. Librarian'),
            hire_date DATE NOT NULL,
            last_login DATETIME NOT NULL,
            is_active ENUM('Active', 'Inactive') NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

def get_books():
    return query("SELECT * FROM books")


def get_members():
    return query("SELECT * FROM members")


def get_loans():
    return query("SELECT * FROM loans")


def get_fines():
    return query("SELECT * FROM fines")


def get_staff():
    return query("SELECT * FROM staff")


def has_related_records(table, id_column, id_value, related_tables):
    for tbl, col in related_tables:
        result = query(f"SELECT COUNT(*) AS cnt FROM {tbl} WHERE {col} = %s", (id_value,))
        if result and result[0]['cnt'] > 0:
            return True
    return False


def calculate_fine(loan_id, return_date=None):
    result = query("""
        SELECT l.*, m.full_name
        FROM loans l
        JOIN members m ON l.member_id = m.member_id
        WHERE l.loan_id = %s
    """, (loan_id,))

    if not result:
        return None

    loan = result[0]

    if return_date is None:
        return_date = datetime.now()

    due_date = loan['due_date']

    if return_date > due_date:
        days_overdue = (return_date - due_date).days
        overdue_fine = days_overdue * 5
    else:
        days_overdue = 0
        overdue_fine = 0

    return {
        'loan': loan,
        'days_overdue': days_overdue,
        'overdue_fine': overdue_fine,
        'book_price': DEFAULT_BOOK_PRICE,
        'total_fine': overdue_fine
    }


def create_fine(book_id, member_id, amount, reason, paid=0.00, paid_date=None):
    issued_date = datetime.now()
    sql = """
        INSERT INTO fines (book_id, member_id, amount, reason, issued_date, paid, paid_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    return query(sql, (book_id, member_id, amount, reason, issued_date, paid, paid_date), fetch=False)


def update_loan_return(loan_id, return_date=None):
    if return_date is None:
        return_date = datetime.now()

    loan_data = query("SELECT l.* FROM loans l WHERE l.loan_id = %s", (loan_id,))
    if not loan_data:
        return None

    loan = loan_data[0]

    query("UPDATE loans SET return_date = %s WHERE loan_id = %s", (return_date, loan_id), fetch=False)

    fine_amount = 0
    if return_date > loan['due_date']:
        days_overdue = (return_date - loan['due_date']).days
        fine_amount = days_overdue * 5

    if fine_amount > 0:
        query("""
            INSERT INTO fines (book_id, member_id, amount, reason, issued_date, paid, paid_date)
            VALUES (%s, %s, %s, 'Overdue', %s, 0.00, NULL)
        """, (loan['book_id'], loan['member_id'], fine_amount, return_date), fetch=False)

    return {'fine_amount': fine_amount, 'days_overdue': max(0, (return_date - loan['due_date']).days)}