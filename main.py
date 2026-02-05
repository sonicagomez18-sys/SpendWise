import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. Page Configuration & Sidebar Styling
st.set_page_config(page_title="SpendWise 💰", layout="wide")
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none !important; }
        .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. Database Initialization
def init_db():
    conn = sqlite3.connect('spendwise_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS summary (
        username TEXT, date TEXT, budget REAL, bills REAL, travel REAL, misc REAL, balance REAL
    )''')
    conn.commit()
    return conn, c

conn, c = init_db()

# 3. Session State for Authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# 4. Sidebar Login / User Interface
def login_sidebar():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2845/2845874.png", width=80)
    st.sidebar.title("🔐 User Access")
    
    if not st.session_state.logged_in:
        tab1, tab2 = st.sidebar.tabs(["Login 🔑", "Sign Up ✨"])
        with tab1:
            u = st.text_input("Username", key="l_user")
            p = st.text_input("Password", type="password", key="l_pass")
            if st.button("Login"):
                user = c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        with tab2:
            new_u = st.text_input("New Username", key="s_user")
            new_p = st.text_input("New Password", type="password", key="s_pass")
            if st.button("Register"):
                try:
                    c.execute("INSERT INTO users VALUES (?, ?)", (new_u, new_p))
                    conn.commit()
                    st.success("✅ Account created! Please login.")
                except:
                    st.error("⚠️ Username already taken.")
    else:
        st.sidebar.write(f"👋 Welcome back, **{st.session_state.username}**!")
        if st.sidebar.button("Logout 🚪"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
        
        st.sidebar.divider()
        st.sidebar.title("🚀 Navigate")
        return st.sidebar.radio("Go to", ["Home 🏠", "Tracker 💸", "Analytics 📊", "Reports 📄"])
    return None

# 5. Main App Functions
def home():
    st.title("💰 SpendWise: Your Financial Assistant")
    st.subheader(f"Hello {st.session_state.username if st.session_state.username else 'Guest'}! ✨")
    
    st.markdown("""
    Take control of your money with **SpendWise**. 🏦
    
    ---
    ### 🛠️ Features you'll love:
    * **Personalized Profiles 👤**: Your data is locked behind your login.
    * **Daily Tracking 💸**: Quickly log bills, travel, and more.
    * **Visual Insights 📈**: Beautiful charts to show where your money goes.
    * **Data Export 📥**: Take your reports with you in CSV format.
    
    *Please log in via the sidebar to access your private dashboard.*
    """)
    st.info("💡 **Pro-Tip:** Consistency is key! Log your expenses every evening to stay on top of your goals.")

def expense_tracker():
    st.title("💸 Daily Expense Tracker")
    today = datetime.now().strftime("%Y-%m-%d")
    
    with st.form("expense_entry"):
        st.write("### Add Today's Spending 📝")
        budget = st.number_input("Monthly Budget (₹)", min_value=0.0, value=50000.0)
        col1, col2, col3 = st.columns(3)
        with col1: bills = st.number_input("Bills (₹) 🏠", min_value=0.0)
        with col2: travel = st.number_input("Travel (₹) 🚗", min_value=0.0)
        with col3: misc = st.number_input("Misc (₹) 🎈", min_value=0.0)
        
        submitted = st.form_submit_button("Save Entry 💾")
        if submitted:
            total = bills + travel + misc
            bal = budget - total
            c.execute("INSERT INTO summary VALUES (?, ?, ?, ?, ?, ?, ?)", 
                      (st.session_state.username, today, budget, bills, travel, misc, bal))
            conn.commit()
            st.success(f"🎉 Success! Remaining balance: ₹{bal:,.2f}")

def analytic():
    st.title("📊 Your Analytics Dashboard")
    df = pd.read_sql_query("SELECT * FROM summary WHERE username=?", conn, params=(st.session_state.username,))
    
    if df.empty:
        st.warning("📭 No data found. Start tracking your expenses to see magic happen!")
    else:
        st.subheader("Spending Breakdown by Category 🥧")
        st.bar_chart(df[['bills', 'travel', 'misc']])
        
        st.subheader("Balance Progress Over Time 📉")
        st.line_chart(df['balance'])

def report():
    st.title("📄 Reports & History")
    df = pd.read_sql_query("SELECT * FROM summary WHERE username=?", conn, params=(st.session_state.username,))
    
    if not df.empty:
        st.write("### Your Transaction Log 📒")
        st.dataframe(df.drop(columns=['username']), use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Report (CSV)",
            data=csv,
            file_name=f"SpendWise_{st.session_state.username}.csv",
            mime="text/csv"
        )
    else:
        st.info("📜 Your history is empty. Time to log your first expense!")

# 6. App Execution Logic
choice = login_sidebar()

if not st.session_state.logged_in:
    home()
else:
    if choice == "Home 🏠": home()
    elif choice == "Tracker 💸": expense_tracker()
    elif choice == "Analytics 📊": analytic()
    elif choice == "Reports 📄": report()