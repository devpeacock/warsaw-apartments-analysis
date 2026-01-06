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

# Geodata path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
WARSAW_DISTRICTS_PATH = PROJECT_ROOT / "data" / "reference" / "warsaw_districts.geojson"


REQUIRED_COLS = {
    "listing_id",
    "city",
    "listing_type",
    "area_m2",
    "price",
    "month",
    "market",
}


BOOL_COLS = [
    "has_parking_space",
    "has_balcony",
    "has_elevator",
    "has_security",
    "has_storage_room",
]

INT_COLS = [
    "rooms",
    "floor",
    "floors_total",
    "build_year",
]

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


def _coerce_bool_series(s: pd.Series) -> pd.Series:
    """
    Robust boolean coercion for typical encodings: True/False, 1/0, "true"/"false", "yes"/"no".
    Unknowns -> <NA>.
    """
    if s.dtype == "bool":
        return s

    # Handle numeric 0/1
    if pd.api.types.is_numeric_dtype(s):
        return s.map({1: True, 0: False}).astype("boolean")

    # Handle strings
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
    required = {fingerprint_col, month_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns for within-month deduplication: {sorted(missing)}")

    before = len(df)

    df = df.sort_values(list(sort_cols), ascending=False)
    df = df.drop_duplicates(subset=[fingerprint_col, month_col], keep="first")

    after = len(df)
    if after != before:
        # Keep this print lightweight; you can switch to logging later.
        print(f"[cleaning] within-month dedup removed {before - after:,} rows ({before:,} → {after:,})")

    return df


def clean_base(df: pd.DataFrame) -> pd.DataFrame:
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

    # Ensure month is datetime (YYYY-MM-01)
    out["month"] = pd.to_datetime(out["month"], errors="coerce")

    # Normalize city names
    out["city"] = normalize_city(out["city"])

    # Numeric coercions
    out["price"] = pd.to_numeric(out["price"], errors="coerce")
    out["area_m2"] = pd.to_numeric(out["area_m2"], errors="coerce")

    for col in INT_COLS:
        if col in out.columns:
            # Use float64 first to allow NaN, will be safer with parquet export
            out[col] = pd.to_numeric(out[col], errors="coerce").astype("float64")
            # Replace sentinel value (-999999) with NaN
            out.loc[out[col] == -999999, col] = np.nan

    for col in FLOAT_COLS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    for col in BOOL_COLS:
        if col in out.columns:
            out[col] = _coerce_bool_series(out[col])

    # Drop rows with invalid essentials
    out = out.dropna(subset=["month", "price", "area_m2", "city", "listing_type", "market"])
    out = out[(out["price"] > 0) & (out["area_m2"] > 0)]

    # Narrow scope to Warsaw only
    out = filter_city(out, city="warszawa")

    # Assign Warsaw district
    out = assign_district_warsaw(
        out,
        districts_path=WARSAW_DISTRICTS_PATH,
        districts_name_col="name",  # GeoJSON column with district name
        out_col="district",
        keep_outside=True,
    )

    # Property fingerprint (used for within-month technical deduplication and downstream analytics)
    cfg = FingerprintConfig(lat_round=4, lon_round=4, area_step=1.0)
    out = add_property_fingerprint(out, cfg, out_col="property_fingerprint")

    # Remove duplicates within the same month only (do NOT remove repetitions across months)
    out = deduplicate_within_month(
        out,
        fingerprint_col="property_fingerprint",
        month_col="month",
        sort_cols=("price",),
    )

    # Derived feature
    out["price_per_m2"] = out["price"] / out["area_m2"]

    return out
