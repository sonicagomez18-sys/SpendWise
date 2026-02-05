import streamlit as st
import sqlite3
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Expense Analytics Dashboard 📊",
    page_icon="📈",
    layout="wide"
)

# 2. Database connection (Updated to match your main app)
conn = sqlite3.connect('spendwise_final.db', check_same_thread=False)

# 3. Security Check
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please log in from the Home page to view your analytics.")
    st.stop()

# 4. Main App
st.title("📊 Your Analytics Dashboard")
st.write(f"Showing data for: **{st.session_state.username}**")

# Query only the logged-in user's data
query = "SELECT * FROM summary WHERE username=?"
df = pd.read_sql_query(query, conn, params=(st.session_state.username,))

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Trend Chart
    st.subheader("📈 Balance Trend Over Time")
    st.line_chart(df.set_index("date")["balance"])

    # Spending Breakdown
    st.subheader("📊 Latest Spending Breakdown")
    latest = df.iloc[-1]

    chart_data = pd.DataFrame({
        "Category": ["Bills", "Travel", "Misc"],
        "Amount": [latest["bills"], latest["travel"], latest["misc"]]
    })
    st.bar_chart(chart_data.set_index("Category"))

    # Dynamic Insights
    st.subheader("📌 Personal Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        if latest["bills"] > (latest["budget"] * 0.5):
            st.warning("⚠️ Bills are consuming more than 50% of your budget.")
        else:
            st.success("✅ Bills are within a healthy range.")
            
    with col2:
        if latest["balance"] < 0:
            st.error("🚨 You have exceeded your budget!")
        elif latest["balance"] < (latest["budget"] * 0.1):
            st.warning("🟡 Careful! Your balance is getting low.")

else:
    st.info("No data available yet. Please log some expenses in the Tracker first!")