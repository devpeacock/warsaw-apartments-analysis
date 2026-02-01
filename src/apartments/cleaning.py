"""
Data Cleaning and Validation Module.

This module provides functions for cleaning, validating, and standardizing
apartment listing data. It handles type coercion, outlier removal, geographic
filtering, and deduplication.

Key Features:
    - Robust type coercion for mixed-type columns
    - Within-month deduplication (preserves cross-month repetitions)
    - Geographic filtering and district assignment for Warsaw
    - Property fingerprinting for duplicate detection
    - Derived feature calculation (price per m²)

Example:
    >>> import pandas as pd
    >>> from apartments.cleaning import clean_base
    >>> 
    >>> raw_df = pd.read_csv('raw_listings.csv')
    >>> clean_df = clean_base(raw_df)
    >>> print(f"Cleaned {len(clean_df)} listings")

Note:
    This module assumes Warsaw-specific geographic data is available at:
    `data/reference/warsaw_districts.geojson`
"""
                                                                                                                                                 
from __future__ import annotations
from pathlib import Path

from duckdb import df
import numpy as np
import pandas as pd
from apartments.fingerprint import FingerprintConfig, add_property_fingerprint
from apartments.location import (
    normalize_city,
    filter_city,
    assign_district_warsaw,
)

# ============================================================================
# Configuration and Constants
# ============================================================================

# Path to Warsaw districts GeoJSON for geographic assignment
# Use current working directory as project root (works for both local and Streamlit Cloud)
import os
PROJECT_ROOT = Path(os.getenv("STREAMLIT_RUNTIME_ROOT", Path.cwd()))
WARSAW_DISTRICTS_PATH = PROJECT_ROOT / "data" / "reference" / "warsaw_districts.geojson"

# Required columns that must be present in raw data
REQUIRED_COLS = {
    "listing_id",
    "city",
    "listing_type",
    "area_m2",
    "price",
    "month",
    "market",
}

# Boolean feature columns (amenities and characteristics)
BOOL_COLS = [
    "has_parking_space",
    "has_balcony",
    "has_elevator",
    "has_security",
    "has_storage_room",
]
# Integer feature columns (discrete numeric values)
INT_COLS = [
    "rooms",
    "floor",
    "floors_total",
    "build_year",
]
# Float feature columns (continuous numeric values)
FLOAT_COLS = [
    "lat",
    "lon",
    "centre_distance",
    "poi_count",
    "school_distance",
    "clinic_distance",
    "post_office_distance",
    "kindergarten_distance",
    "restaurant_distance",
    "college_distance",
    "pharmacy_distance",
]


# ============================================================================
# Helper Functions
# ============================================================================


def _coerce_bool_series(s: pd.Series) -> pd.Series:
    """
    Robust boolean coercion for typical encodings: True/False, 1/0, "true"/"false", "yes"/"no".
    Unknowns -> <NA>.
    """
    # Already boolean dtype - return as is
    if s.dtype == "bool":
        return s

    # Handle numeric 0/1 encoding
    if pd.api.types.is_numeric_dtype(s):
        return s.map({1: True, 0: False}).astype("boolean")

    # Handle string encodings (case-insensitive)
    s_str = s.astype("string").str.strip().str.lower()
    mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
        "y": True,
        "n": False,
        "t": True,
        "f": False,
    }
    return s_str.map(mapping).astype("boolean")


def deduplicate_within_month(
    df: pd.DataFrame,
    *,
    fingerprint_col: str = "property_fingerprint",
    month_col: str = "month",
    sort_cols: tuple[str, ...] = ("price",),
) -> pd.DataFrame:
    """
    Remove duplicate records representing the same property within the same month.

    This step removes technical duplicates inside a monthly snapshot while preserving
    repetitions across different months (which carry information about exposure time).
    """
    # Validate required columns exist
    required = {fingerprint_col, month_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns for within-month deduplication: {sorted(missing)}"
        )

    before = len(df)

    # Sort to control which duplicate is kept (e.g., highest price first)
    df = df.sort_values(list(sort_cols), ascending=False)
    
    # Drop duplicates within same (fingerprint, month)
    df = df.drop_duplicates(subset=[fingerprint_col, month_col], keep="first")

    after = len(df)
    
    # Log deduplication results
    if after != before:
        print(
            f"[cleaning] within-month dedup removed {before - after:,} rows "
            f"({before:,} → {after:,})"
        )

    return df


def clean_base(df: pd.DataFrame, *, districts_path: Path | None = None) -> pd.DataFrame:
    """
    Minimal, reproducible cleaning:
    - validates required columns
    - coerces dtypes (price/area numeric, month datetime, booleans)
    - removes obviously invalid records (price<=0, area<=0)
    - narrows scope to Warsaw
    - assigns Warsaw district (point-in-polygon)
    - builds property fingerprint
    - removes duplicates within the same month (keeps repeats across months)
    - creates price_per_m2
    """
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out = df.copy()

    # Step 2: Parse month column as datetime (YYYY-MM-01 format)
    out["month"] = pd.to_datetime(out["month"], errors="coerce")

    # Step 3: Normalize city names for consistent filtering
    out["city"] = normalize_city(out["city"])

    # Step 4: Coerce core numeric columns
    out["price"] = pd.to_numeric(out["price"], errors="coerce")
    out["area_m2"] = pd.to_numeric(out["area_m2"], errors="coerce")

    # Step 5-6: Coerce integer columns with sentinel value handling
    for col in INT_COLS:
        if col in out.columns:
            # Use float64 to allow NaN representation (safer for parquet export)
            out[col] = pd.to_numeric(out[col], errors="coerce").astype("float64")
            # Replace sentinel value (-999999) with NaN
            out.loc[out[col] == -999999, col] = np.nan

    # Step 7: Coerce float columns
    for col in FLOAT_COLS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # Step 8: Coerce boolean columns with robust encoding handling
    for col in BOOL_COLS:
        if col in out.columns:
            out[col] = _coerce_bool_series(out[col])

    # Step 9: Drop rows with missing critical fields
    out = out.dropna(subset=["month", "price", "area_m2", "city", "listing_type", "market"])
    
    # Step 10: Remove invalid records
    out = out[(out["price"] > 0) & (out["area_m2"] > 0)]

    # Step 11: Filter to Warsaw only
    out = filter_city(out, city="warszawa")

    # Step 12: Assign Warsaw district via geospatial join
    _districts_path = districts_path if districts_path is not None else WARSAW_DISTRICTS_PATH
    out = assign_district_warsaw(
        out,
        districts_path=_districts_path,
        districts_name_col="name",  # GeoJSON column with district name
        out_col="district",
        keep_outside=True,          # Keep listings outside district boundaries
    )

    # Step 13: Generate property fingerprint for deduplication
    cfg = FingerprintConfig(lat_round=4, lon_round=4, area_step=1.0)
    out = add_property_fingerprint(out, cfg, out_col="property_fingerprint")

    # Step 14: Remove within-month duplicates (preserve cross-month repetitions)
    out = deduplicate_within_month(
        out,
        fingerprint_col="property_fingerprint",
        month_col="month",
        sort_cols=("price",),  # Keep highest price when deduplicating
    )

    # Step 15: Calculate derived feature
    out["price_per_m2"] = out["price"] / out["area_m2"]

    return out
