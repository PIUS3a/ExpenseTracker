import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import requests

# -----------------------------------------------------------------------------
# Page & App Configuration
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Expense Tracker", layout="wide")

# -----------------------------------------------------------------------------
# Custom CSS for Styling Dashboard & Sidebar
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Overall Background */
    body {
        background-color: #f4f6f9;
    }
    /* Sidebar with Gradient Background */
    .stSidebar {
        background: linear-gradient(135deg, #00c6ff, #0072ff);
        color: white;
    }
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px 0;
    }
    /* Stylish Offline Error Message */
    .offline-error {
        background-color: #ff4b4b;
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Helper: Check Internet Connection
# -----------------------------------------------------------------------------
def check_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

if not check_internet():
    st.markdown('<div class="offline-error">⚠️ No Internet Connection</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar: Command Info, Profile Picture Upload & Developer Signature
# -----------------------------------------------------------------------------
st.sidebar.info("Run this app with: `streamlit run .\\expensetracker.py`")

st.sidebar.markdown("## Upload Your Profile Picture")
# Provide a file uploader for custom profile picture
custom_profile = st.sidebar.file_uploader("Upload Custom Profile Picture", type=["png", "jpg", "jpeg"], key="custom_profile")
if custom_profile is not None:
    try:
        profile_pic_image = Image.open(custom_profile)
        st.session_state.profile_image = profile_pic_image
    except Exception as e:
        st.error("Error loading custom profile picture: " + str(e))
else:
    # Set default profile picture if none is uploaded
    if "profile_image" not in st.session_state:
        st.session_state.profile_image = "https://upload.wikimedia.org/wikipedia/commons/5/50/Emoji_u1f600.svg"

st.sidebar.image(st.session_state.profile_image, width=100)

st.sidebar.markdown("---")
st.sidebar.markdown("**Developer:** Pius Das")

# -----------------------------------------------------------------------------
# Sidebar: Custom Banner Upload (for Home Page)
# -----------------------------------------------------------------------------
custom_banner = st.sidebar.file_uploader("Upload Custom Banner", type=["png", "jpg", "jpeg"], key="banner")
if custom_banner is not None:
    try:
        banner_image = Image.open(custom_banner)
        st.session_state.banner_image = banner_image
    except Exception as e:
        st.error("Error loading banner image: " + str(e))
elif "banner_image" not in st.session_state:
    st.session_state.banner_image = "https://via.placeholder.com/800x200.png?text=Expense+Tracker"

# -----------------------------------------------------------------------------
# Session State: Expense Data Storage & Monthly Budget
# -----------------------------------------------------------------------------
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = 1000.0  # default monthly budget

# -----------------------------------------------------------------------------
# Helper Functions for Expense Operations
# -----------------------------------------------------------------------------
def add_expense(date, category, amount, description):
    """Append a new expense record."""
    new_entry = pd.DataFrame([[date, category, amount, description]], 
                             columns=st.session_state.expenses.columns)
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_entry], ignore_index=True)

def load_expenses_from_file(key_suffix=""):
    """Load expenses from an uploaded CSV file."""
    uploaded_file = st.file_uploader("Upload your expenses CSV", type=["csv"], key="load_csv" + key_suffix)
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        required_cols = {"Date", "Category", "Amount", "Description"}
        if required_cols.issubset(df.columns):
            st.session_state.expenses = df
            st.success("Expenses loaded successfully!")
        else:
            st.error("CSV file missing required columns: Date, Category, Amount, Description.")

def save_expenses_to_file():
    """Save the current expenses to a CSV file."""
    if not st.session_state.expenses.empty:
        st.session_state.expenses.to_csv("expenses.csv", index=False)
        st.success("Expenses saved to 'expenses.csv'!")
    else:
        st.warning("No expense data available to save.")

def download_expenses():
    """Provide a download button for the expenses CSV."""
    if not st.session_state.expenses.empty:
        csv = st.session_state.expenses.to_csv(index=False).encode("utf-8")
        st.download_button("Download Expenses CSV", data=csv, file_name="expenses.csv", mime="text/csv")
    else:
        st.warning("No expense data to download!")

def show_visualizations():
    """Display interactive charts: bar chart and line chart."""
    if st.session_state.expenses.empty:
        st.warning("No expenses data available for visualization.")
        return

    # Ensure Date column is datetime type
    if not pd.api.types.is_datetime64_any_dtype(st.session_state.expenses["Date"]):
        st.session_state.expenses["Date"] = pd.to_datetime(st.session_state.expenses["Date"], errors='coerce')
    
    # Aggregate only the 'Amount' column for charts
    cat_summary = st.session_state.expenses.groupby("Category", as_index=False)["Amount"].sum()
    fig_bar = px.bar(cat_summary, x="Category", y="Amount", 
                     title="Total Expenses by Category", color="Category")
    
    time_summary = st.session_state.expenses.groupby("Date", as_index=False)["Amount"].sum().sort_values("Date")
    fig_line = px.line(time_summary, x="Date", y="Amount", 
                       title="Expenses Over Time", markers=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("By Category")
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        st.subheader("Over Time")
        st.plotly_chart(fig_line, use_container_width=True)

def reset_data():
    """Clear all expense records."""
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
    st.success("Expense data has been reset.")

def load_sample_data():
    """Load sample expense data to ensure the app isn’t blank."""
    sample_data = pd.DataFrame({
        "Date": ["2025-01-01", "2025-01-02", "2025-01-03"],
        "Category": ["Food", "Transport", "Entertainment"],
        "Amount": [15.75, 7.80, 22.50],
        "Description": ["Breakfast", "Bus fare", "Movie ticket"]
    })
    st.session_state.expenses = sample_data
    st.success("Sample expense data loaded!")

# -----------------------------------------------------------------------------
# Sidebar Navigation
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
page = st.sidebar.selectbox("Go to", 
    ["Home", "Add Expense", "View Expenses", "Visualizations", "Download Data", "Settings"])

# -----------------------------------------------------------------------------
# Main Page Content
# -----------------------------------------------------------------------------
if page == "Home":
    st.title("📊 Expense Tracker Dashboard")
    st.markdown(
        """
        Track your daily expenses and gain insights into your spending habits.
        Use the navigation panel to add new expenses, review your records, or explore interactive charts.
        """
    )
    st.image(st.session_state.banner_image, use_container_width=True)
    
    # Dashboard Metrics in Stylish Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        total_expense = st.session_state.expenses["Amount"].sum()
        st.markdown(f'<div class="metric-card">💰<br><strong>Total Expenses</strong><br>${total_expense:,.2f}</div>', unsafe_allow_html=True)
    with col2:
        num_expenses = st.session_state.expenses.shape[0]
        st.markdown(f'<div class="metric-card">📄<br><strong>Transactions</strong><br>{num_expenses}</div>', unsafe_allow_html=True)
    with col3:
        num_categories = st.session_state.expenses["Category"].nunique() if not st.session_state.expenses.empty else 0
        st.markdown(f'<div class="metric-card">📂<br><strong>Categories</strong><br>{num_categories}</div>', unsafe_allow_html=True)
    
    # Monthly Budget Display and Progress Bar
    if not st.session_state.expenses.empty:
        df = st.session_state.expenses.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        current_month = pd.Timestamp.now().month
        current_year = pd.Timestamp.now().year
        monthly_expenses = df[(df["Date"].dt.month == current_month) & (df["Date"].dt.year == current_year)]["Amount"].sum()
    else:
        monthly_expenses = 0.0
    budget = st.session_state.monthly_budget
    progress = monthly_expenses / budget if budget > 0 else 0
    progress = progress if progress <= 1 else 1
    st.markdown(f'<div class="metric-card">📅<br><strong>Monthly Budget</strong><br>Budget: ${budget:,.2f}<br>Used: ${monthly_expenses:,.2f}</div>', unsafe_allow_html=True)
    st.progress(progress)

elif page == "Add Expense":
    st.title("➕ Add a New Expense")
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Expense Date")
            category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Other"])
        with col2:
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            description = st.text_area("Description")
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            add_expense(date, category, amount, description)
            st.success("Expense added successfully!")

elif page == "View Expenses":
    st.title("📋 Expenses Overview")
    if st.session_state.expenses.empty:
        st.info("No expense data available. Load sample data or add expenses!")
    st.dataframe(st.session_state.expenses, use_container_width=True)
    st.markdown("### CSV File Operations")
    col_csv1, col_csv2 = st.columns(2)
    with col_csv1:
        load_expenses_from_file(key_suffix="view")
    with col_csv2:
        if st.button("Save Expenses"):
            save_expenses_to_file()

elif page == "Visualizations":
    st.title("📈 Expense Visualizations")
    show_visualizations()

elif page == "Download Data":
    st.title("💾 Download Your Expense Data")
    download_expenses()

elif page == "Settings":
    st.title("⚙️ Settings & About")
    st.markdown(
        """
        **Reset Data:** Use the button below to clear all current expense records.  
        **Load Sample Data:** Click below to load sample expense data (ensures the app output isn’t blank).  
        
        ### Set Monthly Budget
        Adjust your monthly budget for expense tracking.
        """
    )
    # Monthly Budget Setting
    monthly_budget = st.number_input("Set your monthly budget", min_value=0.0, value=st.session_state.monthly_budget, key="monthly_budget_input")
    st.session_state.monthly_budget = monthly_budget
    
    st.markdown("---")
    # CSV File Operations: Two columns (Add and Delete)
    csv_col1, csv_col2 = st.columns(2)
    with csv_col1:
        load_expenses_from_file(key_suffix="settings")
    with csv_col2:
        if st.button("Delete CSV Data"):
            reset_data()
    st.markdown("---")
    if st.button("Reset Expense Data"):
        reset_data()
    if st.button("Load Sample Data"):
        load_sample_data()
    st.markdown(
        """
        ---  
        **About:**  
        Developed as a final year project by **Pius Das**.  
        Demonstrates practical skills in Python, data analysis, and interactive web app design.
        """
    )

# -----------------------------------------------------------------------------
# Footer: Developer Signature
# -----------------------------------------------------------------------------
footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    text-align: center;
    font-size: 0.8rem;
    color: gray;
    padding: 0.5rem;
}
</style>
<div class="footer">
    Developed by Pius Das &mdash; © 2025
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
