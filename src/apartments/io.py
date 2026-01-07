"""
Data Loading and I/O Module.

Handles loading raw CSV data from monthly apartment listings and saving/loading
processed parquet datasets. Standardizes column names and extracts temporal metadata.
"""

from pathlib import Path
import pandas as pd
import re

# ============================================================================
# Path Configuration
# ============================================================================

DATA_RAW = Path("data/raw")
SALE_PATH = DATA_RAW / "sale"      # Sale listings by month
RENT_PATH = DATA_RAW / "rent"      # Rental listings by month

# ============================================================================
# Column Schema Mapping
# ============================================================================

# Maps raw CSV column names to standardized schema
COLUMN_MAPPING = {
    "id": "listing_id",
    "city": "city",
    "type": "listing_type",
    "squareMeters": "area_m2",
    "rooms": "rooms",
    "floor": "floor",
    "floorCount": "floors_total",
    "buildYear": "build_year",
    "latitude": "lat",
    "longitude": "lon",
    "centreDistance": "centre_distance",
    "poiCount": "poi_count",
    "schoolDistance": "school_distance",
    "clinicDistance": "clinic_distance",
    "postOfficeDistance": "post_office_distance",
    "kindergartenDistance": "kindergarten_distance",
    "restaurantDistance": "restaurant_distance",
    "collegeDistance": "college_distance",
    "pharmacyDistance": "pharmacy_distance",
    "ownership": "ownership",
    "buildingMaterial": "building_material",
    "condition": "condition",
    "hasParkingSpace": "has_parking_space",
    "hasBalcony": "has_balcony",
    "hasElevator": "has_elevator",
    "hasSecurity": "has_security",
    "hasStorageRoom": "has_storage_room",
    "price": "price",
}


# ============================================================================
# Helper Functions
# ============================================================================

def _extract_month_from_filename(filename: str) -> pd.Timestamp:
    """
    Extract YYYY_MM from filename and return month as Timestamp (YYYY-MM-01).
    Example: sale_2023_01.csv -> 2023-01-01
    """
    match = re.search(r"(20\d{2})[_-](\d{2})", filename)
    if not match:
        raise ValueError(f"Cannot extract month from filename: {filename}")

    year, month = match.groups()
    return pd.Timestamp(f"{year}-{month}-01")


def _standardize_columns(df: pd.DataFrame, column_mapping: dict) -> pd.DataFrame:
    """
    Rename columns to a common schema.
    """
    return df.rename(columns=column_mapping)


# ============================================================================
# Core Data Loaders
# ============================================================================

def load_sale_monthly() -> pd.DataFrame:
    """
    Load monthly SALE data, add month column, unify schema,
    return long-format DataFrame.
    """
    dfs = []

    for file in SALE_PATH.glob("*.csv"):
        df = pd.read_csv(file)

        # Add temporal and market metadata
        df["month"] = _extract_month_from_filename(file.name)
        df["market"] = "sale"

        # Standardize column names
        df = _standardize_columns(df, COLUMN_MAPPING)

        dfs.append(df)

    if not dfs:
        raise ValueError("No sale files found")

    return pd.concat(dfs, ignore_index=True)


def load_rent_monthly() -> pd.DataFrame:
    """
    Load monthly RENT data, add month column, unify schema,
    return long-format DataFrame.
    """
    dfs = []

    for file in RENT_PATH.glob("*.csv"):
        df = pd.read_csv(file)

        # Add temporal and market metadata
        df["month"] = _extract_month_from_filename(file.name)
        df["market"] = "rent"

        # Standardize column names
        df = _standardize_columns(df, COLUMN_MAPPING)

        dfs.append(df)

    if not dfs:
        raise ValueError("No rent files found")

    return pd.concat(dfs, ignore_index=True)


# ============================================================================
# Processed Data Storage
# ============================================================================

DATA_PROCESSED = Path("data/processed")
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)


def save_processed(df: pd.DataFrame, name: str) -> Path:
    """
    Save a cleaned dataset to parquet in data/processed/.
    """
    path = DATA_PROCESSED / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path


def load_processed(name: str) -> pd.DataFrame:
    """
    Load a processed parquet dataset from data/processed/.
    """
    path = DATA_PROCESSED / f"{name}.parquet"
    return pd.read_parquet(path)

