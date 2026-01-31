import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import matplotlib.pyplot as plt
import sys

# -----------------------------
# MAKE 'ml' PACKAGE VISIBLE
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from ml.forecasting import run_forecast
from ml.segmentation import segment_users
from ml.explainability import train_explainable_model
import shap

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Food Delivery Analytics Dashboard",
    layout="wide"
)

# -----------------------------
# LOAD DATA (ROBUST PATH HANDLING)
# -----------------------------
@st.cache_data
def load_data():
    DATA_PATH = BASE_DIR / "output" / "final_food_delivery_dataset.csv"

    if not DATA_PATH.exists():
        st.error(f"Dataset not found at {DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"], format="%d-%m-%Y")
    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🎛 Filters")

selected_city = st.sidebar.multiselect(
    "Select City",
    sorted(df["city"].unique()),
    default=sorted(df["city"].unique())
)

selected_membership = st.sidebar.multiselect(
    "Membership Type",
    sorted(df["membership"].unique()),
    default=sorted(df["membership"].unique())
)

filtered_df = df[
    (df["city"].isin(selected_city)) &
    (df["membership"].isin(selected_membership))
]

# -----------------------------
# KPI SECTION
# -----------------------------
st.title("🍔 Food Delivery Analytics Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📦 Total Orders", filtered_df.shape[0])
col2.metric("💰 Total Revenue", f"₹ {filtered_df['total_amount'].sum():,.0f}")
col3.metric("🧾 Avg Order Value", f"₹ {filtered_df['total_amount'].mean():.2f}")

gold_revenue = filtered_df[filtered_df["membership"] == "Gold"]["total_amount"].sum()
total_revenue = filtered_df["total_amount"].sum()
gold_pct = (gold_revenue / total_revenue * 100) if total_revenue > 0 else 0
col4.metric("⭐ Gold Revenue %", f"{gold_pct:.1f}%")

# -----------------------------
# ROW 1: TIME SERIES ANALYSIS
# -----------------------------
orders_time = (
    filtered_df
    .groupby(filtered_df["order_date"].dt.to_period("M"))
    .size()
    .reset_index(name="orders")
)

orders_time["order_date"] = orders_time["order_date"].astype(str)

fig_time = px.line(
    orders_time,
    x="order_date",
    y="orders",
    title="📈 Monthly Order Trend",
    markers=True
)

st.plotly_chart(fig_time, width='stretch')

# -----------------------------
# ROW 2: CITY & CUISINE PERFORMANCE
# -----------------------------
col5, col6 = st.columns(2)

city_revenue = (
    filtered_df.groupby("city")["total_amount"]
    .sum()
    .reset_index()
    .sort_values("total_amount")
)

fig_city = px.bar(
    city_revenue,
    x="total_amount",
    y="city",
    orientation="h",
    title="🏙 Revenue by City",
    color="total_amount",
    color_continuous_scale="Blues"
)

col5.plotly_chart(fig_city, width='stretch')

cuisine_revenue = (
    filtered_df.groupby("cuisine")["total_amount"]
    .sum()
    .reset_index()
)

fig_cuisine = px.treemap(
    cuisine_revenue,
    path=["cuisine"],
    values="total_amount",
    title="🍽 Cuisine Revenue Share"
)

col6.plotly_chart(fig_cuisine, width='stretch')

# -----------------------------
# ROW 3: MEMBERSHIP ANALYSIS
# -----------------------------
membership_stats = (
    filtered_df.groupby("membership")["total_amount"]
    .agg(Order_Count="count", Avg_Order_Value="mean", Revenue="sum")
    .reset_index()
)

fig_membership = px.bar(
    membership_stats,
    x="membership",
    y="Revenue",
    text_auto=".2s",
    title="👑 Revenue by Membership Type",
    color="membership"
)

st.plotly_chart(fig_membership, width='stretch')

# -----------------------------
# ROW 4: RATING VS REVENUE
# -----------------------------
fig_rating = px.scatter(
    filtered_df,
    x="rating",
    y="total_amount",
    color="membership",
    size="total_amount",
    hover_data=["restaurant_name_y", "city", "cuisine"],
    title="⭐ Rating vs Order Value",
    opacity=0.6
)

st.plotly_chart(fig_rating, width='stretch')

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown(
    "📌 **Hackathon Note:** This dashboard uses the final dataset as the *single source of truth* "
    "for all insights, trends, and conclusions."
)

# -----------------------------
# REVENUE FORECAST
# -----------------------------
st.header("🔮 Revenue Forecast")

forecast, model = run_forecast(filtered_df, periods=30)

fig_forecast = px.line(
    forecast,
    x="ds",
    y=["yhat", "yhat_upper", "yhat_lower"],
    title="30-Day Revenue Forecast"
)

st.plotly_chart(fig_forecast, width='stretch')

# -----------------------------
# USER SEGMENTATION
# -----------------------------
st.header("👥 User Segmentation")

user_segments = segment_users(filtered_df)

fig_segment = px.scatter(
    user_segments,
    x="total_spent",
    y="total_orders",
    color="segment",
    size="avg_order_value",
    title="User Segments (Spending vs Orders)",
    hover_data=["avg_rating"]
)

st.plotly_chart(fig_segment, width='stretch')

# -----------------------------
# EXPLAINABILITY (SHAP)
# -----------------------------
st.header("🧠 Explainability (SHAP)")

shap_values, features = train_explainable_model(filtered_df)

fig, ax = plt.subplots()
shap.plots.bar(shap_values, show=False)
st.pyplot(fig)
