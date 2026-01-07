"""
Warsaw Apartments Price Analysis Package.

Main package for data processing, visualization, and analysis.
"""

__version__ = "0.1.0"

# Core data processing
from .cleaning import clean_base
from .fingerprint import add_property_fingerprint
from .io import load_sale_monthly, load_rent_monthly, save_processed

# Visualization
from .viz import (
    build_view,
    plot_hist,
    plot_box,
    plot_box_by_category,
    plot_scatter,
    apply_dashboard_theme,
)

# Location utilities
from .location import assign_districts

# Labels and mappings
from .labels import build_display_to_raw_map, column_label

# Rental yield calculations
from .rental_yield import make_yield_df, yield_summary

__all__ = [
    # Data processing
    "clean_base",
    "add_property_fingerprint",
    "load_sale_monthly",
    "load_rent_monthly",
    "save_processed",
    # Visualization
    "build_view",
    "plot_hist",
    "plot_box",
    "plot_box_by_category",
    "plot_scatter",
    "apply_dashboard_theme",
    # Location
    "assign_districts",
    # Labels
    "build_display_to_raw_map",
    "column_label",
    # Rental yield
    "make_yield_df",
    "yield_summary",
]
