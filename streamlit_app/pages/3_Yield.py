"""Rental yield analysis dashboard comparing rent and sale prices by category."""

# streamlit_app/pages/3_Yield.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Add streamlit_app and src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from components.loaders import load_sale_static, load_rent_static
from components.sidebar import render_sidebar
from components.ui import inject_global_css, header, kpi_card, card
from apartments.viz import build_view, apply_dashboard_theme
from apartments.rental_yield import make_yield_df, yield_summary
from apartments.labels import label_for_value, column_label
import numpy as np


# ============================================================================
# Helper Functions - Data Binning
# ============================================================================

def create_floor_bins(df):
    """Create floor bins: 0-5, 5-10, 10-15, 15-20, 20+"""
    if 'floor' not in df.columns:
        return df
    df = df.copy()
    df['floor_bin'] = pd.cut(
        df['floor'], 
        bins=[-np.inf, 5, 10, 15, 20, np.inf],
        labels=['0-5', '5-10', '10-15', '15-20', '20+'],
        include_lowest=True
    )
    return df

def create_floors_total_bins(df):
    """Create total floors bins: 0-5, 5-10, 10-15, 15-20, 20+"""
    if 'floors_total' not in df.columns:
        return df
    df = df.copy()
    df['floors_total_bin'] = pd.cut(
        df['floors_total'],
        bins=[-np.inf, 5, 10, 15, 20, np.inf],
        labels=['0-5', '5-10', '10-15', '15-20', '20+'],
        include_lowest=True
    )
    return df

def create_build_year_bins(df):
    """Create build year bins: before 1900, 1900-1950, 1950-1980, then every 10 years"""
    if 'build_year' not in df.columns:
        return df
    df = df.copy()
    bins = [-np.inf, 1900, 1950, 1980, 1990, 2000, 2010, 2020, np.inf]
    labels = ['Before 1900', '1900-1950', '1950-1980', '1980-1990', '1990-2000', '2000-2010', '2010-2020', '2020+']
    df['build_year_bin'] = pd.cut(
        df['build_year'],
        bins=bins,
        labels=labels,
        include_lowest=True
    )
    return df


# ============================================================================
# Page Setup
# ============================================================================

inject_global_css()
header("Yield", "Rental yield proxy analysis by category")


# ============================================================================
# Data Loading and Filtering
# ============================================================================

df_sale = load_sale_static()
df_rent = load_rent_static()

# Apply filters to rental data (yield calculated on rent listings with sale benchmark)
filters = render_sidebar(df_rent)
clip = bool(filters.pop("_clip", True))

df_rent_view, bounds = build_view(
    df_rent,
    filter_spec=filters,
    clip_cols=["price_per_m2", "price", "area_m2"],
    clip=clip,
)

# Create binned columns for better grouping
df_rent_view = create_floor_bins(df_rent_view)
df_rent_view = create_floors_total_bins(df_rent_view)
df_rent_view = create_build_year_bins(df_rent_view)

df_sale = create_floor_bins(df_sale)
df_sale = create_floors_total_bins(df_sale)
df_sale = create_build_year_bins(df_sale)


# ============================================================================
# Category Selection and Yield Calculation
# ============================================================================

# Build list of available categorical columns
available_categories = []
for cat in ["district", "condition", "rooms", "listing_type", "floor_bin", "floors_total_bin", "build_year_bin"]:
    if cat in df_rent_view.columns:
        available_categories.append(cat)

# User selects grouping category
category = st.selectbox(
    "Group by",
    available_categories,
    index=0 if "district" in available_categories else 0,
)

# Calculate yield by comparing rent to sale prices within each category
df_yield = make_yield_df(df_sale, df_rent_view, category=category)
summary = yield_summary(df_yield, group_col=category).reset_index()

# Filter groups with minimum observations
min_n = 10
summary = summary[summary["n"] >= min_n].copy()


# ============================================================================
# KPI Cards
# ============================================================================

k1, k2, k3 = st.columns(3)

with k1:
    kpi_card("Listings (rent)", f"{len(df_rent_view):,}", "After filters")

with k2:
    kpi_card("Yield median", f"{summary['median'].median():.2f}%", "Across groups")

with k3:
    kpi_card("Groups", f"{len(summary):,}", f"Min {min_n} obs")

st.markdown("")

st.markdown("")


# ============================================================================
# Yield Visualization by Category
# ============================================================================

with card():
    st.markdown("### Gross yield proxy by category")
    st.caption(f"Median gross rental yield estimated by {column_label(category)}. Adjust min observations to filter small groups.")
    
    # Map raw values to display labels for better chart readability
    summary_display = summary.copy()
    summary_display[category] = summary_display[category].apply(lambda v: label_for_value(category, str(v)))
    
    # Create bar chart sorted by median yield
    fig = px.bar(
        summary_display.sort_values("median", ascending=False),
        x=category,
        y="median",
        hover_data=["n", "p25", "p75", "mean"],
    )
    apply_dashboard_theme(fig, f"Gross yield proxy – median by {column_label(category)}")
    fig.update_xaxes(title=column_label(category))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ============================================================================
# Summary Table
# ============================================================================

with st.expander("Table"):
    st.dataframe(summary.sort_values("median", ascending=False), use_container_width=True)
