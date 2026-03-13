# ============================================================
#  Personal Finance Dashboard  —  Built with Streamlit
#  Run it with:  streamlit run finance_dashboard.py
# ============================================================
#
#  HOW IT WORKS (quick map of the file):
#  1. IMPORTS & SETUP       — load libraries, page config
#  2. SAMPLE DATA           — demo transactions to start with
#  3. DATA HELPERS          — functions that crunch numbers
#  4. SIDEBAR               — add a transaction + upload CSV
#  5. MAIN PAGE             — summary cards, charts, table
#
# ============================================================


# ── 1. IMPORTS & SETUP ──────────────────────────────────────

import streamlit as st       # the web-app framework
import pandas as pd           # for handling data tables
import plotly.express as px   # for charts
from io import StringIO       # helps read uploaded CSV text

# Page configuration (must be the very first Streamlit call)
st.set_page_config(
    page_title="My Finance Dashboard",
    page_icon="💰",
    layout="wide",
)

# A little CSS to tighten up spacing
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; }
        .metric-container { background: #1e1e2e; border-radius: 12px; padding: 1rem; }
    </style>
""", unsafe_allow_html=True)


# ── 2. SAMPLE DATA ──────────────────────────────────────────
# This gives you something to look at right away.
# Once you import your own CSV or add entries, this stays
# in the background as a fallback demo.

SAMPLE_DATA = [
    {"date": "2025-01-05", "type": "Income",  "category": "Salary",        "description": "January paycheck",   "amount": 4200},
    {"date": "2025-01-10", "type": "Expense", "category": "Housing",       "description": "Rent",               "amount": 1400},
    {"date": "2025-01-15", "type": "Expense", "category": "Food",          "description": "Groceries",          "amount": 180},
    {"date": "2025-02-05", "type": "Income",  "category": "Salary",        "description": "February paycheck",  "amount": 4200},
    {"date": "2025-02-10", "type": "Expense", "category": "Transport",     "description": "Car insurance",      "amount": 220},
    {"date": "2025-02-20", "type": "Income",  "category": "Freelance",     "description": "Design project",     "amount": 800},
    {"date": "2025-02-25", "type": "Expense", "category": "Entertainment", "description": "Concert tickets",    "amount": 95},
    {"date": "2025-03-05", "type": "Income",  "category": "Salary",        "description": "March paycheck",     "amount": 4200},
    {"date": "2025-03-11", "type": "Expense", "category": "Health",        "description": "Gym membership",     "amount": 45},
    {"date": "2025-03-18", "type": "Expense", "category": "Shopping",      "description": "New shoes",          "amount": 130},
]


# ── 3. DATA HELPERS ─────────────────────────────────────────
# These are plain Python functions — good place to learn
# how pandas works before adding complexity.

def load_data(extra_rows=None):
    """
    Turn the sample data (a list of dicts) into a pandas DataFrame.
    If the user has added or uploaded rows, merge them in too.
    """
    df = pd.DataFrame(SAMPLE_DATA)

    if extra_rows:                          # user-added entries
        df = pd.concat([df, pd.DataFrame(extra_rows)], ignore_index=True)

    # Make sure 'date' is a real date (not just a string)
    df["date"] = pd.to_datetime(df["date"])

    # Add a "Month" column so we can group by month in charts
    df["month"] = df["date"].dt.to_period("M").astype(str)

    return df


def compute_summary(df):
    """
    Returns total income, total expenses, and net savings.
    We filter by the 'type' column, then sum 'amount'.
    """
    total_income   = df[df["type"] == "Income"]["amount"].sum()
    total_expenses = df[df["type"] == "Expense"]["amount"].sum()
    net_savings    = total_income - total_expenses
    return total_income, total_expenses, net_savings


def monthly_bar_chart(df):
    """
    Groups data by month and type (Income / Expense),
    then draws a grouped bar chart with Plotly.
    """
    monthly = (
        df.groupby(["month", "type"])["amount"]
        .sum()
        .reset_index()
    )
    fig = px.bar(
        monthly,
        x="month", y="amount", color="type",
        barmode="group",
        color_discrete_map={"Income": "#4ade80", "Expense": "#f87171"},
        labels={"amount": "Amount ($)", "month": "Month", "type": ""},
        title="Monthly Income vs Expenses",
    )
    fig.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="#e2e8f0",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def expense_pie_chart(df):
    """
    Filters to expenses only, groups by category,
    and draws a donut chart.
    """
    expenses = df[df["type"] == "Expense"]
    by_cat = expenses.groupby("category")["amount"].sum().reset_index()

    fig = px.pie(
        by_cat,
        names="category", values="amount",
        hole=0.45,
        title="Expenses by Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="#e2e8f0",
    )
    return fig


# ── 4. SIDEBAR ──────────────────────────────────────────────
# The sidebar is where users interact:
#   (a) manually add a transaction
#   (b) upload a CSV file

# st.session_state persists data between reruns of the app.
# Think of it as the app's "memory" while it's open.
# We use setdefault() to safely initialize it — works across all Python versions.
st.session_state.setdefault("extra_rows", [])

with st.sidebar:
    st.title("💰 Finance Tracker")
    st.markdown("---")

    # ── (a) Manual entry form ──
    st.subheader("➕ Add a Transaction")

    with st.form("add_transaction", clear_on_submit=True):
        date        = st.date_input("Date")
        entry_type  = st.selectbox("Type", ["Income", "Expense"])
        category    = st.selectbox("Category", [
            "Salary", "Freelance", "Investment", "Other Income",   # income
            "Housing", "Food", "Transport", "Entertainment",        # expense
            "Health", "Utilities", "Shopping", "Other",
        ])
        description = st.text_input("Description")
        amount      = st.number_input("Amount ($)", min_value=0.0, step=10.0)
        submitted   = st.form_submit_button("Add Entry")

        if submitted:
            if amount > 0 and description:
                st.session_state.extra_rows.append({
                    "date":        str(date),
                    "type":        entry_type,
                    "category":    category,
                    "description": description,
                    "amount":      amount,
                })
                st.success("Entry added! ✓")
            else:
                st.warning("Please fill in description and amount.")

    st.markdown("---")

    # ── (b) CSV Upload ──
    st.subheader("📂 Import a CSV")
    st.caption("CSV must have columns: date, type, category, description, amount")

    uploaded = st.file_uploader("Choose a .csv file", type="csv")
    if uploaded:
        try:
            csv_df = pd.read_csv(StringIO(uploaded.read().decode("utf-8")))
            # Validate required columns
            required = {"date", "type", "category", "description", "amount"}
            if not required.issubset(csv_df.columns):
                st.error(f"Missing columns. Need: {required}")
            else:
                st.session_state.extra_rows.extend(csv_df.to_dict("records"))
                st.success(f"Imported {len(csv_df)} rows ✓")
        except Exception as e:
            st.error(f"Could not read file: {e}")

    st.markdown("---")

    # Quick reset button (clears manually added rows)
    if st.button("🔄 Reset to Sample Data"):
        st.session_state.extra_rows = []


# ── 5. MAIN PAGE ────────────────────────────────────────────

df = load_data(st.session_state.extra_rows)
total_income, total_expenses, net_savings = compute_summary(df)

st.title("My Finance Dashboard")
st.caption(f"Tracking {len(df)} transactions · {df['date'].min().strftime('%b %Y')} → {df['date'].max().strftime('%b %Y')}")

# ── Summary Cards ──
# st.metric shows a big number with an optional delta (change indicator)
col1, col2, col3 = st.columns(3)
col1.metric("💵 Total Income",   f"${total_income:,.0f}")
col2.metric("💸 Total Expenses", f"${total_expenses:,.0f}")
col3.metric(
    "🏦 Net Savings",
    f"${net_savings:,.0f}",
    delta=f"${net_savings:,.0f}",           # shows green/red arrow
    delta_color="normal",
)

st.markdown("---")

# ── Charts ──
chart_left, chart_right = st.columns(2)

with chart_left:
    st.plotly_chart(monthly_bar_chart(df), use_container_width=True)

with chart_right:
    st.plotly_chart(expense_pie_chart(df), use_container_width=True)

st.markdown("---")

# ── Transaction Table ──
st.subheader("📋 All Transactions")

# Filter controls above the table
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    type_filter = st.multiselect(
        "Filter by type", ["Income", "Expense"], default=["Income", "Expense"]
    )
with filter_col2:
    cat_filter = st.multiselect(
        "Filter by category", sorted(df["category"].unique()), default=list(df["category"].unique())
    )

# Apply filters using pandas boolean indexing
filtered = df[df["type"].isin(type_filter) & df["category"].isin(cat_filter)]

# Sort newest first, format the date nicely for display
filtered_display = filtered.sort_values("date", ascending=False).copy()
filtered_display["date"] = filtered_display["date"].dt.strftime("%Y-%m-%d")
filtered_display["amount"] = filtered_display["amount"].apply(lambda x: f"${x:,.2f}")

st.dataframe(
    filtered_display[["date", "type", "category", "description", "amount"]],
    use_container_width=True,
    hide_index=True,
)

# ── Download button ──
# Lets users export their full dataset as CSV
csv_export = df.drop(columns=["month"]).to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download all transactions as CSV",
    data=csv_export,
    file_name="my_finances.csv",
    mime="text/csv",
)