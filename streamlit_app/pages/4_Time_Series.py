"""Time series dashboard showing month-over-month trends for sale, rent, and yield metrics."""

# streamlit_app/pages/4_Time_Series.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Add streamlit_app and src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from components.loaders import (
    load_mart_city_month_sale,
    load_mart_city_month_rent,
    load_mart_city_month_yield_proxy,
)
from components.ui import inject_global_css, header, kpi_card, card
from apartments.viz import apply_dashboard_theme


# ============================================================================
# Helper Functions - Trend Calculation
# ============================================================================

def calculate_mom_trend(df, col):
    """Calculate month-over-month percentage change for time series data."""
    if len(df) < 2:
        return None
    latest = df[col].iloc[-1]
    prev = df[col].iloc[-2]
    if prev == 0 or pd.isna(latest) or pd.isna(prev):
        return None
    return ((latest - prev) / prev) * 100


# ============================================================================
# Page Setup
# ============================================================================

inject_global_css()
header("Time Series", "Month-over-month trends for sale, rent, and yield")


# ============================================================================
# Data Loading
# ============================================================================

sale = load_mart_city_month_sale()
rent = load_mart_city_month_rent()
yld = load_mart_city_month_yield_proxy()


# ============================================================================
# KPI Cards with Trends
# ============================================================================

# Calculate month-over-month trends for latest period
trend_sale_ppm2 = calculate_mom_trend(sale, 'median_ppm2')
trend_rent_ppm2 = calculate_mom_trend(rent, 'median_ppm2')
trend_yield = calculate_mom_trend(yld, 'gross_yield_proxy')

k1, k2, k3 = st.columns(3)

with k1:
    kpi_card("Months", f"{sale['month'].nunique():,}", "Data points")

with k2:
    kpi_card("Latest sale median/m²", f"{sale['median_ppm2'].iloc[-1]:,.0f} PLN", "Most recent", trend=trend_sale_ppm2)

with k3:
    kpi_card("Latest yield proxy", f"{(yld['gross_yield_proxy'].iloc[-1] * 100):.2f}%", "Most recent", trend=trend_yield)

st.markdown("")

st.markdown("")


# ============================================================================
# Time Series Visualizations
# ============================================================================

# Sale price per m² trend
with card():
    st.markdown("### Sale: median price per m²")
    st.caption("Monthly trend of median sale price per square meter in Warsaw.")
    fig = px.line(sale, x="month", y="median_ppm2")
    apply_dashboard_theme(fig, "Sale: median price per m²")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown("")

# Rent price per m² trend
with card():
    st.markdown("### Rent: median rent per m²")
    st.caption("Monthly trend of median rent per square meter in Warsaw.")
    fig = px.line(rent, x="month", y="median_ppm2")
    apply_dashboard_theme(fig, "Rent: median rent per m²")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown("")

# Gross yield proxy trend
with card():
    st.markdown("### Yield proxy (gross, %)")
    st.caption("Monthly trend of estimated gross rental yield (rent/sale price ratio).")
    # Convert to percentage for better readability
    yld_plot = yld.copy()
    yld_plot["gross_yield_pct"] = yld_plot["gross_yield_proxy"] * 100
    fig = px.line(yld_plot, x="month", y="gross_yield_pct")
    apply_dashboard_theme(fig, "Yield proxy (gross, %)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
