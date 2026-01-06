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
    Extract month timestamp from filename pattern.
    
    Args:
        filename: Filename with pattern *_YYYY_MM.csv or *_YYYY-MM.csv
        
    Returns:
        Timestamp representing first day of month (YYYY-MM-01)
        
    Raises:
        ValueError: If filename doesn't match expected pattern
        
    Example:
        >>> _extract_month_from_filename("sale_2023_01.csv")
        Timestamp('2023-01-01 00:00:00')
    """
    match = re.search(r"(20\d{2})[_-](\d{2})", filename)
    if not match:
        raise ValueError(f"Cannot extract month from filename: {filename}")

    year, month = match.groups()
    return pd.Timestamp(f"{year}-{month}-01")


def _standardize_columns(df: pd.DataFrame, column_mapping: dict) -> pd.DataFrame:
    """
    Rename DataFrame columns to standardized schema.
    
    Args:
        df: DataFrame with raw column names
        column_mapping: Dict mapping raw names to standard names
        
    Returns:
        DataFrame with renamed columns
    """
    return df.rename(columns=column_mapping)


# ============================================================================
# Core Data Loaders
# ============================================================================

def load_sale_monthly() -> pd.DataFrame:
    """
    Load all monthly sale listing CSV files.
    
    Reads all CSV files from data/raw/sale/, extracts month from filename,
    adds market='sale' column, and standardizes column names.
    
    Returns:
        Concatenated DataFrame with all sale listings in long format
        
    Raises:
        ValueError: If no CSV files found in sale directory
        
    Example:
        >>> df = load_sale_monthly()
        >>> df['market'].unique()
        array(['sale'], dtype=object)
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
    Load all monthly rental listing CSV files.
    
    Reads all CSV files from data/raw/rent/, extracts month from filename,
    adds market='rent' column, and standardizes column names.
    
    Returns:
        Concatenated DataFrame with all rental listings in long format
        
    Raises:
        ValueError: If no CSV files found in rent directory
        
    Example:
        >>> df = load_rent_monthly()
        >>> df['market'].unique()
        array(['rent'], dtype=object)
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
    Save DataFrame to parquet in processed data directory.
    
    Args:
        df: DataFrame to save
        name: Base filename (without extension)
        
    Returns:
        Path to saved parquet file
        
    Example:
        >>> path = save_processed(df, "sale_clean")
        >>> print(path)
        data/processed/sale_clean.parquet
    """
    path = DATA_PROCESSED / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path


def load_processed(name: str) -> pd.DataFrame:
    """
    Load DataFrame from parquet in processed data directory.
    
    Args:
        name: Base filename (without extension)
        
    Returns:
        Loaded DataFrame
        
    Example:
        >>> df = load_processed("sale_clean")
    """
    path = DATA_PROCESSED / f"{name}.parquet"
    return pd.read_parquet(path)

