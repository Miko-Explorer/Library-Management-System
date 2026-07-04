import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
from database import get_books, get_connection, has_related_records

def show():
    tab1, tab2, tab3 = st.tabs(["View Books", "Add Book", "Update / Delete"])

    with tab1:
        books = get_books()
        if books:
            df_books = pd.DataFrame(books)
            st.dataframe(df_books, use_container_width=True, hide_index=True)
        else:
            st.info("No books in the library yet.")

    with tab2:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Add New Book")

            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Book Title", placeholder="Enter book title...", key="add_book_title")
                genre = st.selectbox("Genre", [
                    "Action Adventure", "Classics", "Fantasy", "Graphic Novels",
                    "Historical Fiction", "Horror", "Mystery", "Romance",
                    "Sci-Fi", "Suspense/Thriller"
                ], key="add_book_genre")
            with col2:
                year = st.number_input("Year Published", min_value=1000, max_value=datetime.now().year, step=1, key="add_book_year")

            if st.button("Add Book", type="primary", key="add_book_btn"):
                if not title:
                    st.error("Book title is required.")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO books (book_title, book_genre, year_published)
                            VALUES (%s, %s, %s)
                        """, (title, genre, year))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.toast(f"Book '{title}' added successfully!", icon="✅")
                        st.rerun()
                    except mysql.connector.IntegrityError:
                        st.error("A book with this title already exists.")
                    except Exception as e:
                        st.error(f"Error adding book: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        books = get_books()
        if books:
            book_options = {b['book_id']: f"{b['book_title']} ({b['book_id']})" for b in books}
            selected_id = st.selectbox("Select a book to update or delete", list(book_options.keys()),
                                       format_func=lambda x: book_options[x], key="book_select")

            if selected_id:
                selected_book = next((b for b in books if b['book_id'] == selected_id), None)
                if selected_book:
                    with st.container():
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.subheader("Update Book")

                        genre_list = [
                            "Action Adventure", "Classics", "Fantasy", "Graphic Novels",
                            "Historical Fiction", "Horror", "Mystery", "Romance",
                            "Sci-Fi", "Suspense/Thriller"
                        ]
                        current_genre = selected_book['book_genre']
                        if current_genre not in genre_list:
                            genre_list.append(current_genre)
                        try:
                            genre_index = genre_list.index(current_genre)
                        except ValueError:
                            genre_index = 0

                        col1, col2 = st.columns(2)
                        with col1:
                            upd_title = st.text_input("Title", value=selected_book['book_title'], key="upd_book_title")
                            upd_genre = st.selectbox("Genre", genre_list, index=genre_index, key="upd_book_genre")
                        with col2:
                            upd_year = st.number_input("Year Published", min_value=1000, max_value=datetime.now().year,
                                                       value=int(selected_book['year_published']), step=1, key="upd_book_year")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Update Book", type="primary", key="upd_book_btn"):
                                try:
                                    conn = get_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("""
                                        UPDATE books
                                        SET book_title = %s, book_genre = %s, year_published = %s
                                        WHERE book_id = %s
                                    """, (upd_title, upd_genre, upd_year, selected_id))
                                    conn.commit()
                                    cursor.close()
                                    conn.close()
                                    st.toast("Book updated successfully!", icon="✅")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating book: {e}")
                        with col2:
                            if st.button("Delete Book", type="primary", key="del_book_btn"):
                                if has_related_records("books", "book_id", selected_id, [("loans", "book_id"), ("fines", "book_id")]):
                                    st.error("Cannot delete this book because it has associated loans or fines. Please remove those records first.")
                                else:
                                    try:
                                        conn = get_connection()
                                        cursor = conn.cursor()
                                        cursor.execute("DELETE FROM books WHERE book_id = %s", (selected_id,))
                                        conn.commit()
                                        cursor.close()
                                        conn.close()
                                        st.toast("Book deleted successfully!", icon="✅")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error deleting book: {e}")
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No books available to update or delete.")