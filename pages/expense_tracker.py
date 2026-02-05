import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="SpendWise 💰", page_icon="💸", layout="wide")

# 2. Database Setup (UNIFIED to spendwise_final.db)
conn = sqlite3.connect('spendwise_final.db', check_same_thread=False)
c = conn.cursor()

# 3. Sidebar & User Authentication Check
# Assuming the login logic is in your main entry point, we check session state
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.sidebar.warning("Please log in to continue.")
    st.title("🔐 Access Restricted")
    st.info("Use the login sidebar on the main page to access SpendWise.")
    st.stop()

user = st.session_state.username

# 4. Page Functions
def home():
    st.title(f"💰 Welcome back, {user}!")
    st.markdown("""
    **SpendWise** helps you track your daily expenses and visualize your financial health.  
    - Record your daily expenses in **Expense Tracker 💸** - View trends and insights in **Analytics Dashboard 📊** - Access your history and download reports in **Reports & History 📄** """)

def expense_tracker():
    st.title("💸 Daily Expense Tracker")
    today = datetime.now().strftime("%Y-%m-%d")
    
    with st.container(border=True):
        monthly_budget = st.number_input("Monthly Budget (₹)", min_value=0.0, value=50000.0)
        col1, col2, col3 = st.columns(3)
        with col1: bills = st.number_input("Bills (₹)", min_value=0.0)
        with col2: travel = st.number_input("Travel (₹)", min_value=0.0)
        with col3: misc = st.number_input("Misc (₹)", min_value=0.0)

        total_spent = bills + travel + misc
        balance = monthly_budget - total_spent
        st.metric("Remaining Balance", f"₹{balance:,.2f}", delta=balance if balance < 1000 else None)

        if st.button("Save Record", use_container_width=True):
            # Added 'username' to the insert to match your DB schema
            c.execute(
                "INSERT INTO summary (username, date, budget, bills, travel, misc, balance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user, today, monthly_budget, bills, travel, misc, balance)
            )
            conn.commit()
            st.success("✅ Record saved successfully!")

def analytics():
    st.title("📊 Analytics Dashboard")
    df = pd.read_sql_query("SELECT * FROM summary WHERE username=?", conn, params=(user,))
    if df.empty:
        st.info("No records found. Please add expenses first.")
        return

    st.subheader("Spending Overview")
    st.bar_chart(df[['bills','travel','misc']])

    st.subheader("Balance Over Time")
    st.line_chart(df.set_index('date')['balance'])

def reports():
    st.title("📄 Reports & History")
    df = pd.read_sql_query("SELECT date, budget, bills, travel, misc, balance FROM summary WHERE username=?", conn, params=(user,))
    if df.empty:
        st.info("No records found.")
        return

    st.dataframe(df, use_container_width=True)
    st.download_button(
        label="📥 Download CSV Report",
        data=df.to_csv(index=False),
        file_name=f"{user}_expense_report.csv",
        mime="text/csv"
    )

# 5. Sidebar Navigation
st.sidebar.title(f"👤 {user}")
page = st.sidebar.radio("Navigate", ["Home 🏠", "Expense Tracker 💰", "Analytics 📊", "Reports 📄"])

if "Home" in page: home()
elif "Tracker" in page: expense_tracker()
elif "Analytics" in page: analytics()
elif "Reports" in page: reports()