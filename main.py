import streamlit as st

st.set_page_config(
    page_title="Library Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

from database import init_db

init_db()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 50%, #0d1225 100%);
        min-height: 100vh;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6);
    }

    .css-1d391kg, .css-1lcbmhc {
        background: rgba(10, 14, 26, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #f0f4ff !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }

    .main-header {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }

    .sub-header {
        color: #94a3b8 !important;
        font-weight: 300 !important;
        font-size: 1rem !important;
        margin-top: -0.25rem !important;
    }

    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent) !important;
        margin: 2rem 0 !important;
    }

    .section-divider {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.2), transparent) !important;
        margin: 1.5rem 0 !important;
    }

    .stMarkdown, .stText, .stDataFrame, .stTable {
        color: #e2e8f0 !important;
    }

    label, .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label {
        color: #c8d2e6 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }

    .stTextInput input, .stSelectbox select, .stDateInput input, .stNumberInput input {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #f0f4ff !important;
        padding: 10px 14px !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput input:focus, .stSelectbox select:focus, .stDateInput input:focus, .stNumberInput input:focus {
        border-color: rgba(96, 165, 250, 0.4) !important;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }

    .stButton button {
        background: rgba(96, 165, 250, 0.15) !important;
        border: 1px solid rgba(96, 165, 250, 0.2) !important;
        border-radius: 12px !important;
        color: #f0f4ff !important;
        font-weight: 500 !important;
        padding: 8px 20px !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
    }

    .stButton button:hover {
        background: rgba(96, 165, 250, 0.25) !important;
        border-color: rgba(96, 165, 250, 0.4) !important;
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(96, 165, 250, 0.15);
    }

    .stButton button:active {
        transform: translateY(0px);
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        border: none !important;
        color: white !important;
    }

    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
    }

    .stDataFrame {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        padding: 4px !important;
    }

    .stDataFrame table {
        color: #e2e8f0 !important;
    }

    .stDataFrame thead tr th {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    .stDataFrame tbody tr:hover {
        background: rgba(255, 255, 255, 0.03) !important;
    }

    [data-testid="stMetricValue"] {
        color: #f0f4ff !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 400 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricDelta"] {
        color: #4ade80 !important;
    }

    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        color: #f0f4ff !important;
    }

    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.04) !important;
        border-radius: 12px !important;
        color: #c8d2e6 !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 0 0 12px 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-top: none !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 12px !important;
        color: #94a3b8 !important;
        padding: 8px 20px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #f0f4ff !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .stSelectbox div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    .stMultiSelect [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
    }

    .sidebar-logo {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 1.5rem;
    }

    .sidebar-logo .logo-text {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }

    .sidebar-logo .logo-sub {
        font-size: 0.65rem;
        color: #64748b;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 2px;
    }

    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    .dataframe-container {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 8px;
        overflow: auto;
    }

    .chart-container {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 16px;
    }

    .badge-overdue {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }

    .badge-paid {
        background: rgba(74, 222, 128, 0.15);
        color: #4ade80;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        border: 1px solid rgba(74, 222, 128, 0.15);
    }

    .badge-active {
        background: rgba(74, 222, 128, 0.15);
        color: #4ade80;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        border: 1px solid rgba(74, 222, 128, 0.15);
    }

    .badge-inactive {
        background: rgba(148, 163, 184, 0.15);
        color: #94a3b8;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }

    .footer {
        text-align: center;
        padding: 2rem 0 0.5rem 0;
        color: #475569;
        font-size: 0.7rem;
        letter-spacing: 0.05em;
        border-top: 1px solid rgba(255, 255, 255, 0.04);
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

from dashboard import show as show_dashboard
from books import show as show_books
from members import show as show_members
from loans import show as show_loans
from fines import show as show_fines
from staff import show as show_staff

st.sidebar.markdown("""
<div class="sidebar-logo">
    <div class="logo-text">LIBRARY SYSTEM</div>
    <div class="logo-sub">Management Suite</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

nav_options = [
    "Dashboard",
    "Books",
    "Members",
    "Loans",
    "Fines",
    "Staff"
]

page = st.sidebar.radio(
    "Navigation",
    nav_options,
    index=0,
    label_visibility="collapsed",
    key="nav_radio"
)

st.sidebar.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="padding: 0.5rem 0;">
    <span style="color: #64748b; font-size: 0.7rem; letter-spacing: 0.05em;">DATABASE</span>
    <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
        <span style="display: inline-block; width: 8px; height: 8px; background: #4ade80; border-radius: 50%;"></span>
        <span style="color: #94a3b8; font-size: 0.8rem;">Connected</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="padding: 0.5rem 0; margin-top: 0.5rem;">
    <span style="color: #64748b; font-size: 0.7rem; letter-spacing: 0.05em;">SYSTEM INFO</span>
    <div style="color: #94a3b8; font-size: 0.7rem; margin-top: 4px; line-height: 1.6;">
        v2.0.0<br>
        MySQL • Streamlit
    </div>
</div>
""", unsafe_allow_html=True)

if page == "Dashboard":
    st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Overview of library operations and analytics</div>', unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    show_dashboard()
elif page == "Books":
    st.markdown('<div class="main-header">Books</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage your book collection</div>', unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    show_books()
elif page == "Members":
    st.markdown('<div class="main-header">Members</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage library members</div>', unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    show_members()
elif page == "Loans":
    st.markdown('<div class="main-header">Loans</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage book loans and returns</div>', unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    show_loans()
elif page == "Fines":
    st.markdown('<div class="main-header">Fines</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage fines and penalties</div>', unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    show_fines()
elif page == "Staff":
    st.markdown('<div class="main-header">Staff</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage library staff members</div>', unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    show_staff()

st.markdown("""
<div class="footer">
    Library Management System v2.0 &bull; Built with Streamlit &bull; Data powered by MySQL
</div>
""", unsafe_allow_html=True)