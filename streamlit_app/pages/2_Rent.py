"""Rental listings dashboard page with KPI cards, distribution charts, and rent driver analysis."""

# streamlit_app/pages/2_Rent.py
import streamlit as st
import sys
from pathlib import Path

# Add streamlit_app and src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from components.loaders import load_rent_static
from components.sidebar import render_sidebar
from components.ui import inject_global_css, header, kpi_card, card
from apartments.viz import build_view, plot_hist, plot_box_by_category, plot_scatter
import pandas as pd
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
# Helper Functions - Trend Calculation
# ============================================================================

def calculate_trend(df: pd.DataFrame, metric_func, has_month: bool = True) -> float | None:
    """
    Calculate month-over-month percentage change for a metric.
    
    Compares latest month vs previous month using provided metric function.
    Returns percentage change (e.g., 5.2 for +5.2%) or None if insufficient data.
    """
    if not has_month or 'month' not in df.columns or len(df) == 0:
        return None
    
    # Get unique months and sort
    months = sorted(df['month'].unique())
    if len(months) < 2:
        return None
    
    # Get latest and previous month
    latest_month = months[-1]
    prev_month = months[-2]
    
    # Calculate metrics for both months
    latest_data = df[df['month'] == latest_month]
    prev_data = df[df['month'] == prev_month]
    
    if len(latest_data) == 0 or len(prev_data) == 0:
        return None
    
    latest_value = metric_func(latest_data)
    prev_value = metric_func(prev_data)
    
    if prev_value == 0 or pd.isna(latest_value) or pd.isna(prev_value):
        return None
    
    # Calculate percentage change
    pct_change = ((latest_value - prev_value) / prev_value) * 100
    return pct_change


# ============================================================================
# Page Setup
# ============================================================================

inject_global_css()
header("Rent", "Deep-dive into Warsaw rent listings (filters + distribution + drivers)")


# ============================================================================
# Data Loading and Filtering
# ============================================================================

df_base = load_rent_static()

# Render sidebar filters and extract clip setting
filters = render_sidebar(df_base)
clip = bool(filters.pop("_clip", True))

# Apply filters and compute outlier bounds
df_view, bounds = build_view(
    df_base,
    filter_spec=filters,
    clip_cols=["price_per_m2", "price", "area_m2"],
    clip=clip,
)

# Create binned columns for better grouping
df_view = create_floor_bins(df_view)
df_view = create_floors_total_bins(df_view)
df_view = create_build_year_bins(df_view)


# ============================================================================
# KPI Cards with Trends
# ============================================================================

k1, k2, k3, k4 = st.columns(4)

# Calculate month-over-month trends for each metric
has_month = 'month' in df_view.columns
trend_listings = calculate_trend(df_view, lambda df: len(df), has_month)
trend_ppm2 = calculate_trend(df_view, lambda df: df['price_per_m2'].median(), has_month)
trend_price = calculate_trend(df_view, lambda df: df['price'].median(), has_month)
trend_area = calculate_trend(df_view, lambda df: df['area_m2'].mean(), has_month)

with k1:
    kpi_card("Listings", f"{len(df_view):,}", "After filters", trend=trend_listings)

with k2:
    kpi_card("Median rent / m²", f"{df_view['price_per_m2'].median():,.0f} PLN", "Filtered sample", trend=trend_ppm2)

with k3:
    kpi_card("Median rent", f"{df_view['price'].median():,.0f} PLN", "Filtered sample", trend=trend_price)

with k4:
    kpi_card("Avg. area", f"{df_view['area_m2'].mean():.0f} m²", "Filtered sample", trend=trend_area)

st.markdown("")


# ============================================================================
# Distribution Charts (Rent per m² analysis)
# ============================================================================

c1, c2 = st.columns(2)

with c1:
    with card():
        st.markdown("### Rent per m² distribution")
        st.caption("Histogram with median marker. Outliers can be clipped.")
        fig = plot_hist(
            df_view,
            "price_per_m2",
            bounds=bounds,
            bins=60,
            median_mode="line",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with c2:
    with card():
        st.markdown("### Rent per m² by district")
        st.caption("Boxplots compare distributions across districts (categories with low N are hidden).")

        try:
            fig = plot_box_by_category(
                df_view,
                y_col="price_per_m2",
                category_col="district",
                bounds=bounds,
                min_n=10,
                rotate_x=25,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        except ValueError as e:
            st.info(f"Not enough data for district comparison. ({e})")

st.markdown("")


# ============================================================================
# Rent Drivers Analysis (Scatter + Boxplots)
# ============================================================================

# Define available variables for analysis
SCATTER_X_OPTIONS = {
    "Distance to centre (km)": "centre_distance",   # DEFAULT
    "Area (m²)": "area_m2",
    "Number of rooms": "rooms",
    "Building year": "build_year",
    "Floor": "floor",
    "Floors total": "floors_total",
    "POI count (nearby)": "poi_count",
    "School distance (km)": "school_distance",
    "Clinic distance (km)": "clinic_distance",
    "Post office distance (km)": "post_office_distance",
    "Kindergarten distance (km)": "kindergarten_distance",
    "Restaurant distance (km)": "restaurant_distance",
    "College distance (km)": "college_distance",
    "Pharmacy distance (km)": "pharmacy_distance",
}
SCATTER_X_OPTIONS = {lbl: col for lbl, col in SCATTER_X_OPTIONS.items() if col in df_view.columns}

# Categorical variables for boxplot comparison
BOX_X_OPTIONS = {
    "Listing type": "listing_type",          # DEFAULT
    "District": "district",
    "Ownership": "ownership",
    "Building material": "building_material",
    "Condition": "condition",
    "Floor (binned)": "floor_bin",
    "Total floors (binned)": "floors_total_bin",
    "Build year (binned)": "build_year_bin",
    "Has elevator": "has_elevator",
    "Has balcony": "has_balcony",
    "Has parking space": "has_parking_space",
    "Has security": "has_security",
    "Has storage room": "has_storage_room",
}
BOX_X_OPTIONS = {lbl: col for lbl, col in BOX_X_OPTIONS.items() if col in df_view.columns}

# Set default selections
default_scatter_label = (
    "Distance to centre (km)"
    if "Distance to centre (km)" in SCATTER_X_OPTIONS
    else list(SCATTER_X_OPTIONS.keys())[0]
)

default_box_label = (
    "Build year (binned)"
    if "Build year (binned)" in BOX_X_OPTIONS
    else list(BOX_X_OPTIONS.keys())[0]
)

# Create two-column layout for analysis cards
d1, d2 = st.columns(2)

with d1:
    with card():
        st.markdown("### Continuous relationship (scatter)")
        st.caption("Select X to inspect its relationship with rent per m². Trendline shows OLS fit.")

        scatter_x_label = st.selectbox(
            "X variable",
            options=list(SCATTER_X_OPTIONS.keys()),
            index=list(SCATTER_X_OPTIONS.keys()).index(default_scatter_label),
            key="rent_scatter_x",
        )
        scatter_x_col = SCATTER_X_OPTIONS[scatter_x_label]

        fig = plot_scatter(
            df_view,
            x_col=scatter_x_col,
            y_col="price_per_m2",
            bounds=bounds,
            title=f"Impact of {scatter_x_label.lower()} on rent per m²",
            trendline=True,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with d2:
    with card():
        st.markdown("### Structural differences (boxplots)")
        st.caption("Compare distributions across categories. Categories with low sample size are hidden.")

        box_x_label = st.selectbox(
            "Category",
            options=list(BOX_X_OPTIONS.keys()),
            index=list(BOX_X_OPTIONS.keys()).index(default_box_label),
            key="rent_box_x",
        )
        box_x_col = BOX_X_OPTIONS[box_x_label]

        try:
            fig = plot_box_by_category(
                df_view,
                y_col="price_per_m2",
                category_col=box_x_col,
                bounds=bounds,
                title=f"Rent per m² by {box_x_label.lower()}",
                min_n=30,
                rotate_x=25,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        except ValueError as e:
            st.info(f"Not enough data to display boxplots for this variable. ({e})")
