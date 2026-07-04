import streamlit as st
import pandas as pd
import mysql.connector
import re
from datetime import datetime
from database import get_members, get_connection, has_related_records

def show():
    tab1, tab2, tab3 = st.tabs(["View Members", "Add Member", "Update / Delete"])

    with tab1:
        members = get_members()
        if members:
            df_members = pd.DataFrame(members)
            st.dataframe(df_members, use_container_width=True, hide_index=True)
        else:
            st.info("No members registered yet.")

    with tab2:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Register New Member")

            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name", placeholder="Enter full name...", key="add_member_name")
                email = st.text_input("Email", placeholder="Enter email address...", key="add_member_email")
                phone = st.text_input("Phone", placeholder="Enter 11-digit phone number...", key="add_member_phone")
            with col2:
                address = st.text_input("Address", placeholder="Enter address...", key="add_member_address")
                status = st.selectbox("Status", ["Active", "Inactive"], key="add_member_status")

            if st.button("Register Member", type="primary", key="add_member_btn"):
                if not all([full_name, email, phone, address]):
                    st.error("All fields are required.")
                elif not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                    st.error("Invalid email format.")
                elif not re.match(r"^[0-9]{11}$", phone):
                    st.error("Phone must be exactly 11 digits.")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO members (full_name, email, phone, address, membership_date, is_active)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (full_name, email, phone, address, datetime.now(), status))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.toast(f"Member '{full_name}' registered successfully!", icon="✅")
                        st.rerun()
                    except mysql.connector.IntegrityError as e:
                        if "full_name" in str(e):
                            st.error("A member with this name already exists.")
                        elif "email" in str(e):
                            st.error("A member with this email already exists.")
                        elif "phone" in str(e):
                            st.error("A member with this phone number already exists.")
                        else:
                            st.error(f"Duplicate entry: {e}")
                    except Exception as e:
                        st.error(f"Error registering member: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        members = get_members()
        if members:
            member_options = {m['member_id']: f"{m['full_name']} ({m['member_id']})" for m in members}
            selected_id = st.selectbox("Select a member to update or delete", list(member_options.keys()),
                                       format_func=lambda x: member_options[x], key="member_select")

            if selected_id:
                selected_member = next((m for m in members if m['member_id'] == selected_id), None)
                if selected_member:
                    with st.container():
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.subheader("Update Member")

                        col1, col2 = st.columns(2)
                        with col1:
                            upd_name = st.text_input("Full Name", value=selected_member['full_name'], key="upd_member_name")
                            upd_email = st.text_input("Email", value=selected_member['email'], key="upd_member_email")
                            upd_phone = st.text_input("Phone", value=selected_member['phone'], key="upd_member_phone")
                        with col2:
                            upd_address = st.text_input("Address", value=selected_member['address'], key="upd_member_address")
                            upd_status = st.selectbox("Status", ["Active", "Inactive"],
                                                      index=0 if selected_member['is_active'] == "Active" else 1,
                                                      key="upd_member_status")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Update Member", type="primary", key="upd_member_btn"):
                                if not all([upd_name, upd_email, upd_phone, upd_address]):
                                    st.error("All fields are required.")
                                elif not re.match(r"^[^@]+@[^@]+\.[^@]+$", upd_email):
                                    st.error("Invalid email format.")
                                elif not re.match(r"^[0-9]{11}$", upd_phone):
                                    st.error("Phone must be exactly 11 digits.")
                                else:
                                    try:
                                        conn = get_connection()
                                        cursor = conn.cursor()
                                        cursor.execute("""
                                            UPDATE members
                                            SET full_name = %s, email = %s, phone = %s, address = %s, is_active = %s
                                            WHERE member_id = %s
                                        """, (upd_name, upd_email, upd_phone, upd_address, upd_status, selected_id))
                                        conn.commit()
                                        cursor.close()
                                        conn.close()
                                        st.toast("Member updated successfully!", icon="✅")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating member: {e}")
                        with col2:
                            if st.button("Delete Member", type="primary", key="del_member_btn"):
                                if has_related_records("members", "member_id", selected_id, [("loans", "member_id"), ("fines", "member_id")]):
                                    st.error("Cannot delete this member because they have associated loans or fines. Please remove those records first.")
                                else:
                                    try:
                                        conn = get_connection()
                                        cursor = conn.cursor()
                                        cursor.execute("DELETE FROM members WHERE member_id = %s", (selected_id,))
                                        conn.commit()
                                        cursor.close()
                                        conn.close()
                                        st.toast("Member deleted successfully!", icon="✅")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error deleting member: {e}")
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No members available to update or delete.")