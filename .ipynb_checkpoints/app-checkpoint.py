import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import date

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="South African Retail Sales Analytics",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ South African Retail Sales Analytics")
st.markdown(
    """
    An interactive retail analytics dashboard exploring sales,
    product performance, customer behaviour and regional revenue.
    """
)

st.divider()


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

st.sidebar.header("🔎 Dashboard Filters")

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

st.subheader("📍 Sales Performance by Province")

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

st.plotly_chart(fig_province, use_container_width=True)


# ============================================================
# 9. PRODUCT CATEGORY ANALYSIS
# ============================================================

st.subheader("📦 Product Category Analysis")

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

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

with category_col2:
    fig_category_pie = px.pie(
        category_sales,
        names="product_category",
        values="revenue",
        hole=0.45,
        title="Revenue Share by Category"
    )

    st.plotly_chart(
        fig_category_pie,
        use_container_width=True
    )


# ============================================================
# 10. TOP 10 PRODUCTS
# ============================================================

st.subheader("🏆 Top 10 Products by Revenue")

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

st.plotly_chart(fig_products, use_container_width=True)


# ============================================================
# 11. SALES TREND OVER TIME
# ============================================================

st.subheader("📈 Sales Trend Over Time")

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

st.plotly_chart(fig_trend, use_container_width=True)


# ============================================================
# 12. CUSTOMER TYPE ANALYSIS
# ============================================================

st.subheader("👥 Customer Type Analysis")

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

    st.plotly_chart(
        fig_customer,
        use_container_width=True
    )

with customer_col2:
    fig_customer_pie = px.pie(
        customer_sales,
        names="customer_type",
        values="transactions",
        hole=0.4,
        title="Transactions by Customer Type"
    )

    st.plotly_chart(
        fig_customer_pie,
        use_container_width=True
    )


# ============================================================
# 13. PAYMENT METHOD ANALYSIS
# ============================================================

st.subheader("💳 Payment Method Analysis")

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

st.plotly_chart(fig_payment, use_container_width=True)


# ============================================================
# 14. BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

best_province = province_sales.iloc[0]
best_category = category_sales.iloc[0]
best_product = product_sales.iloc[0]

best_payment = payment_sales.sort_values(
    "transactions", ascending=False
).iloc[0]

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.markdown("**Leading Province**")
    st.write(
        f"{best_province['province']} generated "
        f"R {best_province['revenue']:,.2f} in revenue."
    )

    st.markdown("**Leading Product Category**")
    st.write(
        f"{best_category['product_category']} generated "
        f"R {best_category['revenue']:,.2f} in revenue."
    )

with insight_col2:
    st.markdown("**Top Product**")
    st.write(
        f"{best_product['product_name']} generated "
        f"R {best_product['revenue']:,.2f} in revenue."
    )

    st.markdown("**Most Used Payment Method**")
    st.write(
        f"{best_payment['payment_method']} recorded "
        f"{int(best_payment['transactions']):,} transactions."
    )


# ============================================================
# 15. DATA QUALITY CHECK
# ============================================================

st.divider()
st.subheader("🧹 Data Quality Overview")

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
st.subheader("📋 Retail Sales Records")

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
    label="⬇️ Download Filtered Sales Data",
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
