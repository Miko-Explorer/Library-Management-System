import mysql.connector
from mysql.connector import Error
import streamlit as st
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'miko1605',
    'database': 'library_db',
    'port': 3306
}

DEFAULT_BOOK_PRICE = 500.00


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        st.error(f"Database connection failed: {e}")
        st.stop()


def init_db():
    conn = get_connection()
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


def execute_query(query, params=None, fetch=True):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as e:
        cursor.close()
        conn.close()
        st.error(f"Database error: {e}")
        return None


def get_table_data(table_name, columns="*", condition=None, params=None):
    query = f"SELECT {columns} FROM {table_name}"
    if condition:
        query += f" WHERE {condition}"
    return execute_query(query, params)


def get_books():
    return get_table_data("books")


def get_members():
    return get_table_data("members")


def get_loans():
    return get_table_data("loans")


def get_fines():
    return get_table_data("fines")


def get_staff():
    return get_table_data("staff")


def has_related_records(table, id_column, id_value, related_tables):
    conn = get_connection()
    cursor = conn.cursor()
    for tbl, col in related_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl} WHERE {col} = %s", (id_value,))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.close()
            conn.close()
            return True
    cursor.close()
    conn.close()
    return False


def calculate_fine(loan_id, return_date=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT l.*, m.full_name
        FROM loans l
        JOIN members m ON l.member_id = m.member_id
        WHERE l.loan_id = %s
    """, (loan_id,))
    loan = cursor.fetchone()
    cursor.close()
    conn.close()

    if not loan:
        return None

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
    query = """
        INSERT INTO fines (book_id, member_id, amount, reason, issued_date, paid, paid_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(query, (book_id, member_id, amount, reason, issued_date, paid, paid_date), fetch=False)


def update_loan_return(loan_id, return_date=None):
    if return_date is None:
        return_date = datetime.now()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT l.*
        FROM loans l
        WHERE l.loan_id = %s
    """, (loan_id,))
    loan = cursor.fetchone()

    if not loan:
        cursor.close()
        conn.close()
        return None

    cursor.execute(
        "UPDATE loans SET return_date = %s WHERE loan_id = %s",
        (return_date, loan_id)
    )

    fine_amount = 0
    if return_date > loan['due_date']:
        days_overdue = (return_date - loan['due_date']).days
        fine_amount = days_overdue * 5

    if fine_amount > 0:
        cursor.execute("""
            INSERT INTO fines (book_id, member_id, amount, reason, issued_date, paid, paid_date)
            VALUES (%s, %s, %s, 'Overdue', %s, 0.00, NULL)
        """, (loan['book_id'], loan['member_id'], fine_amount, return_date))

    return {'fine_amount': fine_amount, 'days_overdue': max(0, (return_date - loan['due_date']).days)}