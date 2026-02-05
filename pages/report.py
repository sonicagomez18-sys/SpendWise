import streamlit as st
import sqlite3
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Reports & History 📄",
    page_icon="📝",
    layout="wide"
)

# 2. Database Connection (MATCHES main.py)
conn = sqlite3.connect('spendwise_final.db', check_same_thread=False)

# 3. Security Check
# This ensures the page knows WHO is logged in from the main app
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please log in from the Home page to view your reports.")
    st.stop() 

# 4. Main App Logic
st.title("📄 Your Personal Reports")
st.write(f"Logged in as: **{st.session_state.username}**")

# Use a parameterized query to prevent SQL injection and filter by user
query = "SELECT date, budget, bills, travel, misc, balance FROM summary WHERE username=? ORDER BY date DESC"
df = pd.read_sql_query(query, conn, params=(st.session_state.username,))

if not df.empty:
    st.subheader("📜 Spending History")
    # Display the table
    st.dataframe(df, use_container_width=True)

    # Summary Stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Spent (Bills/Travel/Misc)", f"₹{df[['bills', 'travel', 'misc']].sum().sum():,.2f}")
    
    st.subheader("⬇️ Download Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV Report",
        data=csv,
        file_name=f"SpendWise_{st.session_state.username}_Report.csv",
        mime="text/csv"
    )
else:
    st.info("No records available yet. Go to the Tracker to add your first expense!")