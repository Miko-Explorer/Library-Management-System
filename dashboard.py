import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import get_books, get_members, get_loans, get_fines

def show():
    books = get_books()
    members = get_members()
    loans = get_loans()
    fines = get_fines()

    col1, col2, col3, col4 = st.columns(4)

    total_books = len(books) if books else 0
    total_members = len(members) if members else 0
    active_members = len([m for m in members if m and m.get('is_active') == 'Active']) if members else 0
    total_loans = len(loans) if loans else 0
    active_loans = len([l for l in loans if l and l.get('return_date') is None]) if loans else 0
    total_fines = len(fines) if fines else 0
    unpaid_fines = len([f for f in fines if f and f.get('paid_date') is None]) if fines else 0

    with col1:
        st.metric("Total Books", total_books)
    with col2:
        st.metric("Total Members", total_members, f"{active_members} active")
    with col3:
        st.metric("Active Loans", active_loans, f"{total_loans} total")
    with col4:
        st.metric("Unpaid Fines", unpaid_fines, f"{total_fines} total")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Books by Genre")
        if books:
            genre_counts = {}
            for b in books:
                genre = b.get('book_genre', 'Unknown')
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            if genre_counts:
                df_genre = pd.DataFrame({
                    'Genre': list(genre_counts.keys()),
                    'Count': list(genre_counts.values())
                })
                fig = px.bar(
                    df_genre,
                    x='Genre',
                    y='Count',
                    color='Count',
                    color_continuous_scale='Blues',
                    text='Count'
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#e2e8f0',
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True, key="genre_chart")
            else:
                st.info("No book data available")
        else:
            st.info("No book data available")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Member Status")
        if members:
            active_count = 0
            inactive_count = 0
            for m in members:
                if m and m.get('is_active') == 'Active':
                    active_count += 1
                else:
                    inactive_count += 1
            if active_count + inactive_count > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=['Active', 'Inactive'],
                    values=[active_count, inactive_count],
                    marker=dict(colors=['#4ade80', '#64748b']),
                    textinfo='label+percent',
                    textposition='inside',
                    hole=0.4
                )])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#e2e8f0',
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig, use_container_width=True, key="member_pie")
            else:
                st.info("No member data available")
        else:
            st.info("No member data available")
        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Loans Over Time")
        if loans:
            loan_dates = []
            for l in loans:
                if l and l.get('loan_date'):
                    try:
                        loan_dates.append(l['loan_date'])
                    except:
                        pass
            if loan_dates:
                df_dates = pd.DataFrame({'Date': loan_dates})
                df_dates['Date'] = pd.to_datetime(df_dates['Date'])
                df_dates['Month'] = df_dates['Date'].dt.to_period('M').dt.to_timestamp()
                monthly = df_dates.groupby('Month').size().reset_index(name='Count')
                fig = px.line(
                    monthly,
                    x='Month',
                    y='Count',
                    markers=True,
                    line_shape='spline'
                )
                fig.update_traces(line_color='#60a5fa', marker_color='#60a5fa')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#e2e8f0',
                    xaxis=dict(
                        gridcolor='rgba(255,255,255,0.05)',
                        tickformat='%b %Y'
                    ),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig, use_container_width=True, key="loans_line")
            else:
                st.info("No loan date data available")
        else:
            st.info("No loan data available")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Fine Amounts Distribution")
        if fines:
            amounts = [float(f.get('amount', 0)) for f in fines if f and f.get('amount') is not None]
            if amounts:
                fig = px.histogram(
                    x=amounts,
                    nbins=10,
                    labels={'x': 'Fine Amount (PHP)', 'y': 'Count'},
                    color_discrete_sequence=['#a78bfa']
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#e2e8f0',
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    margin=dict(l=20, r=20, t=30, b=20),
                    bargap=0.1
                )
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig, use_container_width=True, key="fines_hist")
            else:
                st.info("No fine amount data available")
        else:
            st.info("No fine data available")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Recent Loan Activity")
    if loans:
        recent_loans = sorted(loans, key=lambda x: x.get('loan_date', ''), reverse=True)[:5]
        recent_data = []
        for l in recent_loans:
            book = next((b for b in books if b.get('book_id') == l.get('book_id')), {})
            member = next((m for m in members if m.get('member_id') == l.get('member_id')), {})
            recent_data.append({
                'Loan ID': l.get('loan_id'),
                'Book': book.get('book_title', 'Unknown')[:30],
                'Member': member.get('full_name', 'Unknown'),
                'Loan Date': l.get('loan_date'),
                'Due Date': l.get('due_date'),
                'Returned': 'Yes' if l.get('return_date') else 'No'
            })
        if recent_data:
            df_recent = pd.DataFrame(recent_data)
            st.dataframe(df_recent, use_container_width=True, hide_index=True)
        else:
            st.info("No recent loan activity")
    else:
        st.info("No loan data available")