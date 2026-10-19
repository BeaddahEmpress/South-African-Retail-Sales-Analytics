import streamlit as st
import pandas as pd
import html
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from supabase import create_client
from datetime import date

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="South African Retail Sales Analytics",
    layout="wide"
)

# ------------------------------------------------------------
# Theme: periwinkle background, violet / pink / orange / yellow
# accents, with warm browns to keep things calm.
# ------------------------------------------------------------

PERIWINKLE = "#E4E2F5"    # page background
CARD = "#F4F2FD"          # cards and chart panels
CARD_BORDER = "#CFC9EE"
VIOLET = "#5B3FA0"
VIOLET_DARK = "#3B2A7A"
PINK = "#E8589A"
ORANGE = "#F28C28"
YELLOW = "#F6C945"
BLUE = "#4F6BED"
BROWN = "#8A5A3C"
ESPRESSO = "#4A3426"      # body text
LATTE = "#E2D3C4"         # sidebar

SUNSET = [YELLOW, ORANGE, PINK, VIOLET]   # low -> high

pio.templates["friendly"] = go.layout.Template(
    layout=dict(
        font=dict(
            family="Nunito, 'Segoe UI', Helvetica, Arial, sans-serif",
            color=ESPRESSO,
            size=13
        ),
        title=dict(
            font=dict(
                family="Poppins, 'Segoe UI', sans-serif",
                size=18,
                color=VIOLET_DARK
            ),
            x=0.01
        ),
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        colorway=[
            VIOLET, ORANGE, PINK, BLUE, YELLOW,
            BROWN, "#9B7BD6", "#F2A65A", "#C23B7C"
        ],
        xaxis=dict(
            gridcolor="#E3DFF5", linecolor="#B9B2E0",
            zeroline=False, ticks="outside", tickcolor="#B9B2E0"
        ),
        yaxis=dict(
            gridcolor="#E3DFF5", linecolor="#B9B2E0",
            zeroline=False
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(
            bgcolor=VIOLET_DARK,
            font=dict(color="#FFFFFF")
        ),
        margin=dict(l=40, r=20, t=60, b=40)
    )
)
pio.templates.default = "friendly"


def show_chart(fig):
    """Render a Plotly chart using the dashboard theme."""
    fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(selector=dict(type="bar"), marker_line_width=0)
    fig.update_traces(
        selector=dict(type="pie"),
        marker=dict(line=dict(color=CARD, width=3))
    )
    # theme=None stops Streamlit overriding the custom colours.
    st.plotly_chart(fig, use_container_width=True, theme=None)


def insight_card(label, text, colour):
    """Show one business insight as a coloured card."""
    st.markdown(
        f'<div class="insight" style="border-left-color:{colour};">'
        f'<div class="insight-label">{html.escape(label)}</div>'
        f'<div class="insight-text">{text}</div>'
        "</div>",
        unsafe_allow_html=True
    )


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&family=Poppins:wght@500;600;700&display=swap');

/* ---------- Page ---------- */
.stApp {
    background-color: #E4E2F5;
    color: #4A3426;
    font-family: 'Nunito', 'Segoe UI', Helvetica, Arial, sans-serif;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}
.stApp p, .stApp li, .stApp label, .stApp span { color: #4A3426; }
.stApp [data-testid="stCaptionContainer"] { color: #7C6454; }

/* ---------- Hero banner ---------- */
.hero {
    background: linear-gradient(115deg, #4B2FA0 0%, #7A3FB0 38%, #E8589A 72%, #F28C28 100%);
    border-radius: 18px;
    padding: 2.2rem 2.4rem 1.9rem 2.4rem;
    margin-bottom: 1.8rem;
    box-shadow: 0 6px 18px rgba(91, 63, 160, 0.25);
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: "";
    position: absolute;
    right: -60px; top: -70px;
    width: 240px; height: 240px;
    border-radius: 50%;
    background: rgba(246, 201, 69, 0.28);
}
.hero-eyebrow {
    color: #FFE08A !important;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.hero-title {
    font-family: 'Poppins', 'Segoe UI', sans-serif;
    color: #FFFFFF !important;
    font-size: 2.3rem;
    font-weight: 700;
    line-height: 1.2;
    margin: 0 0 0.6rem 0;
}
.hero-text {
    color: #FBEFFA !important;
    font-size: 1.05rem;
    max-width: 720px;
    margin: 0 0 1rem 0;
    position: relative;
    z-index: 1;
}
.hero-tags {
    color: #FFE9C2 !important;
    font-size: 0.85rem;
    letter-spacing: 0.04em;
    position: relative;
    z-index: 1;
}
.hero-bar {
    position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 6px;
    background: #F6C945;
}

/* ---------- Section headings ---------- */
.stApp h3 {
    font-family: 'Poppins', 'Segoe UI', sans-serif;
    color: #3B2A7A;
    font-weight: 600;
    font-size: 1.35rem;
    border-left: 6px solid #E8589A;
    padding-left: 0.7rem;
    margin-top: 0.8rem;
}
hr { border-color: #CFC9EE !important; }

/* ---------- KPI cards ---------- */
div[data-testid="stMetric"] {
    background-color: #F4F2FD;
    border: 1px solid #CFC9EE;
    border-top: 5px solid #5B3FA0;
    padding: 16px 18px;
    border-radius: 14px;
    box-shadow: 0 2px 6px rgba(91, 63, 160, 0.10);
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"] { border-top-color: #F28C28; }
div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"] { border-top-color: #E8589A; }
div[data-testid="stHorizontalBlock"] > div:nth-child(4) div[data-testid="stMetric"] { border-top-color: #F6C945; }
div[data-testid="stMetricLabel"] p {
    color: #7C6454 !important;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
div[data-testid="stMetricValue"] {
    color: #3B2A7A;
    font-family: 'Poppins', 'Segoe UI', sans-serif;
    font-weight: 600;
}

/* ---------- Chart panels ---------- */
div[data-testid="stPlotlyChart"] {
    background: #F4F2FD;
    border: 1px solid #CFC9EE;
    border-radius: 14px;
    padding: 6px;
    box-shadow: 0 2px 6px rgba(91, 63, 160, 0.10);
    overflow: hidden;
}

/* ---------- Insight cards ---------- */
.insight {
    background: #F4F2FD;
    border: 1px solid #CFC9EE;
    border-left: 6px solid #5B3FA0;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(91, 63, 160, 0.08);
}
.insight-label {
    color: #8A5A3C;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.insight-text {
    color: #4A3426;
    font-size: 1rem;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background-color: #E2D3C4;
    border-right: 1px solid #CDB9A6;
}
section[data-testid="stSidebar"] h2 {
    font-family: 'Poppins', 'Segoe UI', sans-serif;
    color: #5B3FA0;
    font-size: 1.4rem;
}
div[data-baseweb="select"] > div,
div[data-baseweb="base-input"],
div[data-baseweb="input"] {
    background-color: #F7F0E8 !important;
    border-color: #CDB9A6 !important;
}
span[data-baseweb="tag"] { background-color: #5B3FA0 !important; }
span[data-baseweb="tag"] span { color: #FFFFFF !important; }
input { color: #4A3426 !important; }

/* ---------- Buttons ---------- */
.stDownloadButton button, .stButton button {
    background-color: #F28C28;
    color: #3A2418;
    border: none;
    border-radius: 999px;
    padding: 0.5rem 1.4rem;
    font-weight: 700;
}
.stDownloadButton button:hover, .stButton button:hover {
    background-color: #E8589A;
    color: #FFFFFF;
}
.stDownloadButton button p, .stButton button p { color: inherit !important; }

/* ---------- Alerts, tables, expander ---------- */
div[data-testid="stAlert"] {
    background-color: #EDE9FA;
    border: 1px solid #CFC9EE;
    border-radius: 12px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #CFC9EE;
    border-radius: 12px;
    overflow: hidden;
}
div[data-testid="stExpander"] {
    background-color: #F4F2FD;
    border: 1px solid #CFC9EE;
    border-radius: 12px;
}
</style>
""",
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero">'
    '<div class="hero-eyebrow">Retail Analytics</div>'
    '<div class="hero-title">South African Retail Sales Analytics</div>'
    '<p class="hero-text">An interactive retail analytics dashboard exploring '
    'sales, product performance, customer behaviour and regional revenue.</p>'
    '<div class="hero-tags">Python &bull; Pandas &bull; Plotly &bull; '
    'Streamlit &bull; Supabase</div>'
    '<div class="hero-bar"></div>'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 2. SUPABASE CONNECTION
# ============================================================

@st.cache_resource
def connect_to_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ============================================================
# 3. LOAD DATA
# ============================================================

@st.cache_data(ttl=300)
def load_data():
    try:
        supabase = connect_to_supabase()

        response = (
            supabase.table("retail_sales")
            .select("*")
            .order("sale_id")
            .limit(1000)
            .execute()
        )

        if response.data:
            df = pd.DataFrame(response.data)
        else:
            st.warning(
                "The retail_sales table is empty. "
                "Loading the local CSV instead."
            )
            df = pd.read_csv("south_african_retail_sales.csv")

    except Exception as error:
        st.warning(
            "Could not load data from Supabase. "
            "Using the local CSV as a fallback."
        )
        st.caption(f"Connection detail: {error}")
        df = pd.read_csv("south_african_retail_sales.csv")

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "Dataset not found. Place "
        "'south_african_retail_sales.csv' in the same "
        "folder as app.py."
    )
    st.stop()

except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()


# ============================================================
# 4. DATA CLEANING AND PREPARATION
# ============================================================

required_columns = [
    "sale_id",
    "sale_date",
    "province",
    "product_category",
    "product_name",
    "customer_type",
    "payment_method",
    "quantity",
    "unit_price",
    "total_sales"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

df = df[required_columns].copy()

df["sale_date"] = pd.to_datetime(
    df["sale_date"], errors="coerce"
)

numeric_columns = [
    "sale_id",
    "quantity",
    "unit_price",
    "total_sales"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column], errors="coerce"
    )

df = df.dropna(
    subset=[
        "sale_id",
        "sale_date",
        "province",
        "product_category",
        "product_name",
        "quantity",
        "unit_price",
        "total_sales"
    ]
)

df = df.drop_duplicates(subset=["sale_id"])

for column in [
    "province",
    "product_category",
    "product_name",
    "customer_type",
    "payment_method"
]:
    df[column] = df[column].astype(str).str.strip()

df = df[
    (df["quantity"] > 0)
    & (df["unit_price"] >= 0)
    & (df["total_sales"] >= 0)
].copy()

# Use the recorded sale total as the revenue measure.
# Flag records where it differs from quantity * unit_price.
df["calculated_sales"] = (
    df["quantity"] * df["unit_price"]
).round(2)

df["sales_mismatch"] = (
    (df["total_sales"] - df["calculated_sales"]).abs()
    > 0.02
)

df["month"] = df["sale_date"].dt.to_period("M").astype(str)
df["year"] = df["sale_date"].dt.year

if df.empty:
    st.error("No valid records remain after data cleaning.")
    st.stop()


# ============================================================
# 5. SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")

st.sidebar.caption(
    "Select the criteria you want to analyse."
)

all_provinces = sorted(df["province"].dropna().unique())
all_categories = sorted(
    df["product_category"].dropna().unique()
)
all_customer_types = sorted(
    df["customer_type"].dropna().unique()
)
all_payment_methods = sorted(
    df["payment_method"].dropna().unique()
)

selected_provinces = st.sidebar.multiselect(
    "Province",
    options=all_provinces,
    default=all_provinces
)

selected_categories = st.sidebar.multiselect(
    "Product Category",
    options=all_categories,
    default=all_categories
)

selected_customer_types = st.sidebar.multiselect(
    "Customer Type",
    options=all_customer_types,
    default=all_customer_types
)

selected_payment_methods = st.sidebar.multiselect(
    "Payment Method",
    options=all_payment_methods,
    default=all_payment_methods
)

min_date = df["sale_date"].min().date()
max_date = df["sale_date"].max().date()

date_range = st.sidebar.date_input(
    "Sale Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range


# ============================================================
# 6. APPLY FILTERS
# ============================================================

filtered_df = df[
    df["province"].isin(selected_provinces)
    & df["product_category"].isin(selected_categories)
    & df["customer_type"].isin(selected_customer_types)
    & df["payment_method"].isin(selected_payment_methods)
    & (df["sale_date"].dt.date >= start_date)
    & (df["sale_date"].dt.date <= end_date)
].copy()

if filtered_df.empty:
    st.warning(
        "No sales match the selected filters. "
        "Adjust the filters in the sidebar."
    )
    st.stop()


# ============================================================
# 7. KEY PERFORMANCE INDICATORS
# ============================================================

total_transactions = len(filtered_df)
total_revenue = filtered_df["total_sales"].sum()
total_units = filtered_df["quantity"].sum()
average_sale = filtered_df["total_sales"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Transactions",
    f"{total_transactions:,}"
)

col2.metric(
    "Total Revenue",
    f"R {total_revenue:,.2f}"
)

col3.metric(
    "Units Sold",
    f"{total_units:,.0f}"
)

col4.metric(
    "Average Sale Value",
    f"R {average_sale:,.2f}"
)

st.divider()


# ============================================================
# 8. SALES BY PROVINCE
# ============================================================

st.subheader("Sales Performance by Province")

province_sales = (
    filtered_df.groupby("province", as_index=False)
    .agg(
        revenue=("total_sales", "sum"),
        transactions=("sale_id", "nunique")
    )
    .sort_values("revenue", ascending=False)
)

fig_province = px.bar(
    province_sales,
    x="province",
    y="revenue",
    color="revenue",
    color_continuous_scale=SUNSET,
    text_auto=".2s",
    title="Revenue by Province",
    labels={
        "province": "Province",
        "revenue": "Revenue (ZAR)"
    },
    hover_data=["transactions"]
)

fig_province.update_layout(
    xaxis_title="Province",
    yaxis_title="Revenue (ZAR)",
    xaxis_tickangle=-35
)

show_chart(fig_province)


# ============================================================
# 9. PRODUCT CATEGORY ANALYSIS
# ============================================================

st.subheader("Product Category Analysis")

category_col1, category_col2 = st.columns(2)

category_sales = (
    filtered_df.groupby("product_category", as_index=False)
    .agg(
        revenue=("total_sales", "sum"),
        units_sold=("quantity", "sum"),
        transactions=("sale_id", "nunique")
    )
    .sort_values("revenue", ascending=False)
)

with category_col1:
    fig_category = px.bar(
        category_sales,
        x="product_category",
        y="revenue",
        color="product_category",
        title="Revenue by Product Category",
        labels={
            "product_category": "Category",
            "revenue": "Revenue (ZAR)"
        }
    )

    fig_category.update_layout(
        showlegend=False,
        xaxis_tickangle=-30
    )

    show_chart(fig_category)

with category_col2:
    fig_category_pie = px.pie(
        category_sales,
        names="product_category",
        values="revenue",
        hole=0.45,
        title="Revenue Share by Category"
    )

    show_chart(fig_category_pie)


# ============================================================
# 10. TOP 10 PRODUCTS
# ============================================================

st.subheader("Top 10 Products by Revenue")

product_sales = (
    filtered_df.groupby(
        ["product_name", "product_category"],
        as_index=False
    )
    .agg(
        revenue=("total_sales", "sum"),
        units_sold=("quantity", "sum"),
        transactions=("sale_id", "nunique")
    )
    .sort_values("revenue", ascending=False)
    .head(10)
)

fig_products = px.bar(
    product_sales.sort_values("revenue"),
    x="revenue",
    y="product_name",
    color="product_category",
    orientation="h",
    title="Best-Performing Products",
    labels={
        "revenue": "Revenue (ZAR)",
        "product_name": "Product",
        "product_category": "Category"
    },
    hover_data=["units_sold", "transactions"]
)

show_chart(fig_products)


# ============================================================
# 11. SALES TREND OVER TIME
# ============================================================

st.subheader("Sales Trend Over Time")

monthly_sales = (
    filtered_df.set_index("sale_date")
    .resample("MS")["total_sales"]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    monthly_sales,
    x="sale_date",
    y="total_sales",
    markers=True,
    title="Monthly Revenue Trend",
    labels={
        "sale_date": "Month",
        "total_sales": "Revenue (ZAR)"
    }
)

fig_trend.update_traces(
    line=dict(color=VIOLET, width=3),
    marker=dict(color=PINK, size=9, line=dict(color=CARD, width=2))
)

show_chart(fig_trend)


# ============================================================
# 12. CUSTOMER TYPE ANALYSIS
# ============================================================

st.subheader("Customer Type Analysis")

customer_sales = (
    filtered_df.groupby("customer_type", as_index=False)
    .agg(
        revenue=("total_sales", "sum"),
        transactions=("sale_id", "nunique"),
        units_sold=("quantity", "sum")
    )
)

customer_col1, customer_col2 = st.columns(2)

with customer_col1:
    fig_customer = px.bar(
        customer_sales,
        x="customer_type",
        y="revenue",
        color="customer_type",
        title="Revenue by Customer Type",
        labels={
            "customer_type": "Customer Type",
            "revenue": "Revenue (ZAR)"
        }
    )

    fig_customer.update_layout(showlegend=False)

    show_chart(fig_customer)

with customer_col2:
    fig_customer_pie = px.pie(
        customer_sales,
        names="customer_type",
        values="transactions",
        hole=0.4,
        title="Transactions by Customer Type"
    )

    show_chart(fig_customer_pie)


# ============================================================
# 13. PAYMENT METHOD ANALYSIS
# ============================================================

st.subheader("Payment Method Analysis")

payment_sales = (
    filtered_df.groupby("payment_method", as_index=False)
    .agg(
        revenue=("total_sales", "sum"),
        transactions=("sale_id", "nunique")
    )
    .sort_values("revenue", ascending=False)
)

fig_payment = px.bar(
    payment_sales,
    x="payment_method",
    y="transactions",
    color="payment_method",
    text="transactions",
    title="Transactions by Payment Method",
    labels={
        "payment_method": "Payment Method",
        "transactions": "Number of Transactions"
    }
)

fig_payment.update_layout(showlegend=False)

show_chart(fig_payment)


# ============================================================
# 14. BUSINESS INSIGHTS
# ============================================================

st.subheader("Business Insights")

best_province = province_sales.iloc[0]
best_category = category_sales.iloc[0]
best_product = product_sales.iloc[0]

best_payment = payment_sales.sort_values(
    "transactions", ascending=False
).iloc[0]

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    insight_card(
        "Leading Province",
        f"<b>{html.escape(str(best_province['province']))}</b> generated "
        f"R {best_province['revenue']:,.2f} in revenue.",
        VIOLET
    )

    insight_card(
        "Leading Product Category",
        f"<b>{html.escape(str(best_category['product_category']))}</b> "
        f"generated R {best_category['revenue']:,.2f} in revenue.",
        PINK
    )

with insight_col2:
    insight_card(
        "Top Product",
        f"<b>{html.escape(str(best_product['product_name']))}</b> "
        f"generated R {best_product['revenue']:,.2f} in revenue.",
        ORANGE
    )

    insight_card(
        "Most Used Payment Method",
        f"<b>{html.escape(str(best_payment['payment_method']))}</b> "
        f"recorded {int(best_payment['transactions']):,} transactions.",
        YELLOW
    )


# ============================================================
# 15. DATA QUALITY CHECK
# ============================================================

st.divider()
st.subheader("Data Quality Overview")

quality_col1, quality_col2, quality_col3 = st.columns(3)

quality_col1.metric(
    "Valid Records",
    f"{len(df):,}"
)

quality_col2.metric(
    "Duplicate Sale IDs Removed",
    f"{0:,}"
)

quality_col3.metric(
    "Sales Calculation Mismatches",
    f"{int(df['sales_mismatch'].sum()):,}"
)

st.caption(
    "The duplicate metric above is a placeholder for removed "
    "duplicate IDs. Calculation mismatches compare recorded "
    "sales against quantity multiplied by unit price."
)

with st.expander("View Data Quality Details"):
    st.write("Missing values remaining:")
    st.dataframe(
        df.isna().sum().rename("missing_values"),
        use_container_width=True
    )

    st.write("Records where total_sales differs from quantity × unit_price:")
    st.dataframe(
        df.loc[
            df["sales_mismatch"],
            [
                "sale_id",
                "quantity",
                "unit_price",
                "total_sales",
                "calculated_sales"
            ]
        ],
        use_container_width=True
    )


# ============================================================
# 16. RAW DATA TABLE
# ============================================================

st.divider()
st.subheader("Retail Sales Records")

st.caption(
    f"Showing {len(filtered_df):,} records matching your filters."
)

display_columns = [
    "sale_id",
    "sale_date",
    "province",
    "product_category",
    "product_name",
    "customer_type",
    "payment_method",
    "quantity",
    "unit_price",
    "total_sales"
]

st.dataframe(
    filtered_df[display_columns].sort_values(
        "sale_date", ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 17. DOWNLOAD FILTERED DATA
# ============================================================

csv_data = filtered_df[display_columns].to_csv(index=False)

st.download_button(
    label="Download Filtered Sales Data",
    data=csv_data,
    file_name="filtered_retail_sales.csv",
    mime="text/csv"
)


# ============================================================
# 18. FOOTER
# ============================================================

st.divider()

st.caption(
    "South African Retail Sales Analytics | "
    "Built with Python, Pandas, Plotly, Streamlit and Supabase."
)
