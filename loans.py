import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import get_loans, get_books, get_members, get_connection, update_loan_return


def show():
    tab1, tab2, tab3 = st.tabs(["View Loans", "New Loan", "Return Book"])

    with tab1:
        loans = get_loans()
        if loans:
            books = get_books()
            members = get_members()
            loan_data = []
            for l in loans:
                book = next((b for b in books if b.get('book_id') == l.get('book_id')), {})
                member = next((m for m in members if m.get('member_id') == l.get('member_id')), {})
                loan_data.append({
                    'Loan ID': l.get('loan_id'),
                    'Book': book.get('book_title', 'Unknown')[:40],
                    'Member': member.get('full_name', 'Unknown'),
                    'Loan Date': l.get('loan_date'),
                    'Due Date': l.get('due_date'),
                    'Return Date': l.get('return_date') or 'Not Returned',
                    'Status': 'Active' if l.get('return_date') is None else 'Returned'
                })
            df_loans = pd.DataFrame(loan_data)
            st.dataframe(df_loans, use_container_width=True, hide_index=True)
        else:
            st.info("No loan records found.")

    with tab2:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Create New Loan")

            books = get_books()
            members = get_members()

            if not books:
                st.warning("No books available. Please add books first.")
            elif not members:
                st.warning("No members registered. Please add members first.")
            else:
                loans = get_loans()
                active_loan_book_ids = [l['book_id'] for l in loans if l.get('return_date') is None] if loans else []

                available_books = [b for b in books if b['book_id'] not in active_loan_book_ids]

                if not available_books:
                    st.warning("No books available for loan. All books are currently checked out.")
                else:
                    book_options = {b['book_id']: f"{b['book_title']} (ID: {b['book_id']})" for b in available_books}
                    member_options = {m['member_id']: f"{m['full_name']} (ID: {m['member_id']})" for m in members}

                    col1, col2 = st.columns(2)
                    with col1:
                        selected_book = st.selectbox("Select Book", list(book_options.keys()),
                                                     format_func=lambda x: book_options[x], key="loan_book")
                        loan_date = st.date_input("Loan Date", datetime.now(), key="loan_date")
                    with col2:
                        selected_member = st.selectbox("Select Member", list(member_options.keys()),
                                                       format_func=lambda x: member_options[x], key="loan_member")

                    due_date = loan_date + timedelta(days=7)
                    st.info(f"Due date will be: {due_date.strftime('%Y-%m-%d')} (7 days from loan date)")

                    if st.button("Issue Loan", type="primary", key="issue_loan_btn"):
                        try:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("""
                                INSERT INTO loans (book_id, member_id, loan_date, due_date, return_date)
                                VALUES (%s, %s, %s, %s, NULL)
                            """, (selected_book, selected_member, loan_date, due_date))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.toast("Loan created successfully! Book due in 7 days.", icon="✅")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating loan: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Return a Book")

            loans = get_loans()
            active_loans = [l for l in loans if l.get('return_date') is None] if loans else []

            if not active_loans:
                st.info("No active loans to return.")
            else:
                books = get_books()
                members = get_members()

                loan_options = {}
                for l in active_loans:
                    book = next((b for b in books if b.get('book_id') == l.get('book_id')), {})
                    member = next((m for m in members if m.get('member_id') == l.get('member_id')), {})
                    label = f"{book.get('book_title', 'Unknown')[:30]} \u2192 {member.get('full_name', 'Unknown')} (ID: {l['loan_id']})"
                    loan_options[l['loan_id']] = label

                selected_loan = st.selectbox("Select active loan to return", list(loan_options.keys()),
                                             format_func=lambda x: loan_options[x], key="return_loan_select")

                return_date = st.date_input("Return Date", datetime.now(), key="return_date")

                if st.button("Process Return", type="primary", key="return_btn"):
                    conn = get_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT due_date FROM loans WHERE loan_id = %s", (selected_loan,))
                    loan_data = cursor.fetchone()
                    cursor.close()
                    conn.close()

                    if loan_data:
                        due = loan_data['due_date']
                        ret = datetime.combine(return_date, datetime.min.time())

                        result = update_loan_return(selected_loan, ret)

                        if result:
                            msg = "Book returned successfully!"
                            if result['days_overdue'] > 0:
                                msg += f" Overdue by {result['days_overdue']} days. Fine: PHP {result['fine_amount']:.2f}"
                            else:
                                msg += " Returned on time. No fine."
                            st.toast(msg, icon="✅")
                            st.rerun()
                        else:
                            st.error("Error processing return.")
            st.markdown('</div>', unsafe_allow_html=True)
