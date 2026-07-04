import streamlit as st
import pandas as pd
from database import get_fines, get_books, get_members, create_fine

def show():
    tab1, tab2 = st.tabs(["View Fines", "Issue Fine"])

    with tab1:
        fines = get_fines()
        if fines:
            books = get_books()
            members = get_members()
            fine_data = []
            for f in fines:
                book = next((b for b in books if b.get('book_id') == f.get('book_id')), {})
                member = next((m for m in members if m.get('member_id') == f.get('member_id')), {})
                fine_data.append({
                    'Fine ID': f.get('fine_id'),
                    'Book': book.get('book_title', 'Unknown')[:30],
                    'Member': member.get('full_name', 'Unknown'),
                    'Amount (PHP)': float(f.get('amount', 0)),
                    'Reason': f.get('reason'),
                    'Issued Date': f.get('issued_date'),
                    'Paid': float(f.get('paid', 0)),
                    'Paid Date': f.get('paid_date') or 'Unpaid',
                    'Status': 'Paid' if f.get('paid_date') else 'Unpaid'
                })
            df_fines = pd.DataFrame(fine_data)
            st.dataframe(df_fines, use_container_width=True, hide_index=True)

            total_unpaid = sum([f.get('amount', 0) - f.get('paid', 0) for f in fines if f.get('paid_date') is None])
            total_paid = sum([f.get('paid', 0) for f in fines if f.get('paid_date') is not None])
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Unpaid Fines", f"PHP {total_unpaid:.2f}")
            with col2:
                st.metric("Total Paid Fines", f"PHP {total_paid:.2f}")
        else:
            st.info("No fine records found.")

    with tab2:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Issue a Fine")

            books = get_books()
            members = get_members()

            if not books:
                st.warning("No books available.")
            elif not members:
                st.warning("No members registered.")
            else:
                book_options = {b['book_id']: f"{b['book_title']} (ID: {b['book_id']})" for b in books}
                member_options = {m['member_id']: f"{m['full_name']} (ID: {m['member_id']})" for m in members}

                col1, col2 = st.columns(2)
                with col1:
                    selected_book = st.selectbox("Book", list(book_options.keys()), format_func=lambda x: book_options[x], key="fine_book")
                    selected_member = st.selectbox("Member", list(member_options.keys()),
                                                   format_func=lambda x: member_options[x], key="fine_member")
                with col2:
                    reason = st.selectbox("Reason", ["Overdue", "Damaged", "Lost"], key="fine_reason")
                    amount = st.number_input("Amount (PHP)", min_value=0.0, value=50.0, step=10.0, key="fine_amount")

                if st.button("Issue Fine", type="primary", key="issue_fine_btn"):
                    try:
                        result = create_fine(selected_book, selected_member, amount, reason)
                        if result:
                            st.toast(f"Fine issued successfully! Amount: PHP {amount:.2f}", icon="✅")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error issuing fine: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
