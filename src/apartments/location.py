from __future__ import annotations
from pathlib import Path
import pandas as pd


def normalize_city(s: pd.Series) -> pd.Series:
    """
    Normalize city names to a canonical lowercase representation.
    """
    return (
        s.astype("string")
         .str.strip()
         .str.lower()
         .str.replace(r"\s+", " ", regex=True)
    )


def filter_city(df: pd.DataFrame, *, city: str) -> pd.DataFrame:
    """
    Filter dataset to a specific city (expects normalized city names).
    """
    if "city" not in df.columns:
        raise ValueError("Missing required column: city")
    return df[df["city"] == city].copy()


def assign_district_warsaw(
    df: pd.DataFrame,
    *,
    districts_path: Path,
    districts_name_col: str,
    out_col: str = "district",
    lat_col: str = "lat",
    lon_col: str = "lon",
    keep_outside: bool = True,
) -> pd.DataFrame:
    """
    Assign Warsaw district using point-in-polygon join.
    """
    import geopandas as gpd

    missing = [c for c in (lat_col, lon_col) if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    x = df.dropna(subset=[lat_col, lon_col]).copy()

    points = gpd.GeoDataFrame(
        x,
        geometry=gpd.points_from_xy(x[lon_col], x[lat_col]),
        crs="EPSG:4326",
    )

    districts = gpd.read_file(districts_path)
    districts = districts[districts[districts_name_col].astype("string").str.lower() != "warszawa"].copy() # Keep only actual districts (without the whole-city polygon)

    if districts.crs is None:
        raise ValueError("Districts file has no CRS.")
    districts = districts.to_crs(points.crs)

    if districts_name_col not in districts.columns:
        raise ValueError(
            f"Column '{districts_name_col}' not found in districts file. "
            f"Available: {list(districts.columns)}"
        )

    joined = gpd.sjoin(
        points,
        districts[[districts_name_col, "geometry"]],
        how="left",
        predicate="within",
    )

    joined[out_col] = (
    joined[districts_name_col]
        .astype("string")
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )



    out = joined.drop(
        columns=["geometry", "index_right", districts_name_col],
        errors="ignore",
    )

    if not keep_outside:
        out = out.dropna(subset=[out_col]).copy()

    return pd.DataFrame(out)