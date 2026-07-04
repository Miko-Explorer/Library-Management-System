import streamlit as st
import pandas as pd
import mysql.connector
import re
from datetime import datetime
from database import get_staff, get_connection

def show():
    tab1, tab2, tab3 = st.tabs(["View Staff", "Add Staff", "Update / Delete"])

    with tab1:
        staff = get_staff()
        if staff:
            df_staff = pd.DataFrame(staff)
            st.dataframe(df_staff, use_container_width=True, hide_index=True)
        else:
            st.info("No staff records found.")

    with tab2:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Add Staff Member")

            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name", placeholder="Enter full name...", key="add_staff_name")
                username = st.text_input("Username", placeholder="Enter username...", key="add_staff_username")
                email = st.text_input("Email", placeholder="Enter email...", key="add_staff_email")
                phone = st.text_input("Phone", placeholder="Enter 11-digit phone...", key="add_staff_phone")
            with col2:
                address = st.text_input("Address", placeholder="Enter address...", key="add_staff_address")
                role = st.selectbox("Role", ["Admin", "Librarian", "Asst. Librarian"], key="add_staff_role")
                hire_date = st.date_input("Hire Date", datetime.now(), key="add_staff_hire")
                status = st.selectbox("Status", ["Active", "Inactive"], key="add_staff_status")

            if st.button("Add Staff", type="primary", key="add_staff_btn"):
                if not all([full_name, username, email, phone, address]):
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
                            INSERT INTO staff (full_name, username, email, phone, address, roles, hire_date, last_login, is_active)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (full_name, username, email, phone, address, role, hire_date, datetime.now(), status))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.toast(f"Staff '{full_name}' added successfully!", icon="✅")
                        st.rerun()
                    except mysql.connector.IntegrityError as e:
                        if "full_name" in str(e):
                            st.error("A staff member with this name already exists.")
                        elif "username" in str(e):
                            st.error("This username is already taken.")
                        elif "email" in str(e):
                            st.error("A staff member with this email already exists.")
                        else:
                            st.error(f"Duplicate entry: {e}")
                    except Exception as e:
                        st.error(f"Error adding staff: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        staff = get_staff()
        if staff:
            staff_options = {s['staff_id']: f"{s['full_name']} ({s['staff_id']})" for s in staff}
            selected_id = st.selectbox("Select staff to update or delete", list(staff_options.keys()),
                                       format_func=lambda x: staff_options[x], key="staff_select")

            if selected_id:
                selected_staff = next((s for s in staff if s['staff_id'] == selected_id), None)
                if selected_staff:
                    with st.container():
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.subheader("Update Staff")

                        col1, col2 = st.columns(2)
                        with col1:
                            upd_name = st.text_input("Full Name", value=selected_staff['full_name'], key="upd_staff_name")
                            upd_username = st.text_input("Username", value=selected_staff['username'], key="upd_staff_username")
                            upd_email = st.text_input("Email", value=selected_staff['email'], key="upd_staff_email")
                            upd_phone = st.text_input("Phone", value=selected_staff['phone'], key="upd_staff_phone")
                        with col2:
                            upd_address = st.text_input("Address", value=selected_staff['address'], key="upd_staff_address")
                            upd_role = st.selectbox("Role", ["Admin", "Librarian", "Asst. Librarian"],
                                                    index=["Admin", "Librarian", "Asst. Librarian"].index(
                                                        selected_staff['roles']),
                                                    key="upd_staff_role")
                            upd_status = st.selectbox("Status", ["Active", "Inactive"],
                                                      index=0 if selected_staff['is_active'] == "Active" else 1,
                                                      key="upd_staff_status")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Update Staff", type="primary", key="upd_staff_btn"):
                                if not all([upd_name, upd_username, upd_email, upd_phone, upd_address]):
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
                                            UPDATE staff
                                            SET full_name = %s, username = %s, email = %s, phone = %s,
                                                address = %s, roles = %s, is_active = %s
                                            WHERE staff_id = %s
                                        """, (upd_name, upd_username, upd_email, upd_phone, upd_address,
                                              upd_role, upd_status, selected_id))
                                        conn.commit()
                                        cursor.close()
                                        conn.close()
                                        st.toast("Staff updated successfully!", icon="✅")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating staff: {e}")
                        with col2:
                            if st.button("Delete Staff", type="primary", key="del_staff_btn"):
                                try:
                                    conn = get_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM staff WHERE staff_id = %s", (selected_id,))
                                    conn.commit()
                                    cursor.close()
                                    conn.close()
                                    st.toast("Staff deleted successfully!", icon="✅")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting staff: {e}")
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No staff available to update or delete.")