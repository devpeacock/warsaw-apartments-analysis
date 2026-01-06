# streamlit_app/pages/1_Sale.py
import streamlit as st
import sys
from pathlib import Path

# Add streamlit_app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.loaders import load_sale_static
from components.sidebar import render_sidebar
from components.ui import inject_global_css, header, kpi_card, card  # <- use context manager

from apartments.viz import (
    build_view,
    plot_hist,
    plot_box_by_category,
    plot_scatter,
)
import pandas as pd
import numpy as np

# Helper functions for binning
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

def calculate_trend(df: pd.DataFrame, metric_func, has_month: bool = True) -> float | None:
    """
    Calculate month-over-month percentage change for a metric.
    
    Args:
        df: DataFrame with 'month' column
        metric_func: Function to calculate metric (e.g., lambda df: df['price'].median())
        has_month: Whether the data has a month column
    
    Returns:
        Percentage change (e.g., 5.2 for +5.2%) or None if not enough data
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

# -------------------------
# Page UI
# -------------------------
inject_global_css()
header("Sale", "Deep-dive into Warsaw sale listings (filters + distribution + drivers)")

# -------------------------
# Data
# -------------------------
df_base = load_sale_static()

filters = render_sidebar(df_base)
clip = bool(filters.pop("_clip", True))

df_view, bounds = build_view(
    df_base,
    filter_spec=filters,
    clip_cols=["price_per_m2", "price", "area_m2"],
    clip=clip,
    p_low=0.01,
    p_high=0.99,
)

# Create binned columns for better grouping
df_view = create_floor_bins(df_view)
df_view = create_floors_total_bins(df_view)
df_view = create_build_year_bins(df_view)

# -------------------------
# KPI cards
# -------------------------
k1, k2, k3, k4 = st.columns(4)

# Calculate trends based on filtered data
has_month = 'month' in df_view.columns
trend_listings = calculate_trend(df_view, lambda df: len(df), has_month)
trend_ppm2 = calculate_trend(df_view, lambda df: df['price_per_m2'].median(), has_month)
trend_price = calculate_trend(df_view, lambda df: df['price'].median(), has_month)
trend_area = calculate_trend(df_view, lambda df: df['area_m2'].mean(), has_month)

with k1:
    kpi_card("Listings", f"{len(df_view):,}", "After filters", trend=trend_listings)

with k2:
    kpi_card("Median price / m²", f"{df_view['price_per_m2'].median():,.0f} PLN", "Filtered sample", trend=trend_ppm2)

with k3:
    kpi_card("Median price", f"{df_view['price'].median():,.0f} PLN", "Filtered sample", trend=trend_price)

with k4:
    kpi_card("Avg. area", f"{df_view['area_m2'].mean():.0f} m²", "Filtered sample", trend=trend_area)

st.markdown("")

# -------------------------
# Distribution section (2 cards)
# -------------------------
c1, c2 = st.columns(2)

with c1:
    with card():
        st.markdown("### Price per m² distribution")
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
        st.markdown("### Price per m² by district")
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

# -------------------------
# Drivers section (2 cards side-by-side, independent controls)
# -------------------------

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
    "Kindergarten distance (km)": "kindergarten_distance",
    "Restaurant distance (km)": "restaurant_distance",
}
SCATTER_X_OPTIONS = {lbl: col for lbl, col in SCATTER_X_OPTIONS.items() if col in df_view.columns}

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

d1, d2 = st.columns(2)

with d1:
    with card():
        st.markdown("### Continuous relationship (scatter)")
        st.caption("Select X to inspect its relationship with price per m². Trendline shows OLS fit.")

        scatter_x_label = st.selectbox(
            "X variable",
            options=list(SCATTER_X_OPTIONS.keys()),
            index=list(SCATTER_X_OPTIONS.keys()).index(default_scatter_label),
            key="sale_scatter_x",
        )
        scatter_x_col = SCATTER_X_OPTIONS[scatter_x_label]

        fig = plot_scatter(
            df_view,
            x_col=scatter_x_col,
            y_col="price_per_m2",
            bounds=bounds,
            title=f"Impact of {scatter_x_label.lower()} on price per m²",
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
            key="sale_box_x",
        )
        box_x_col = BOX_X_OPTIONS[box_x_label]

        try:
            fig = plot_box_by_category(
                df_view,
                y_col="price_per_m2",
                category_col=box_x_col,
                bounds=bounds,
                title=f"Price per m² by {box_x_label.lower()}",
                min_n=30,
                rotate_x=25,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        except ValueError as e:
            st.info(f"Not enough data to display boxplots for this variable. ({e})")


with st.expander("Preview (first 200 rows)"):
    if df_view.empty:
        st.warning("No data to display. Adjust filters.")
    else:
        st.dataframe(df_view.head(200), use_container_width=True, height=400)

with st.expander("Debug"):
    st.write(f"Base: {len(df_base):,} | View: {len(df_view):,}")
    st.write(f"Columns: {len(df_view.columns)} | Shape: {df_view.shape}")

    if len(df_view) == 0 and any(k.startswith("has_") for k in filters):
        st.warning("⚠️ Amenity filters active but result is empty!")
        st.write("Sample values from base data:")
        for col in ["has_elevator", "has_balcony", "has_parking_space"]:
            if col in df_base.columns:
                vals = df_base[col].value_counts().head(5)
                st.write(f"  {col}: {vals.to_dict()}")

    active = {k: v for k, v in filters.items() if v not in (None, [], (), "")}
    st.json(active if active else {"filters": "none"})


# streamlit run streamlit_app/app.py
