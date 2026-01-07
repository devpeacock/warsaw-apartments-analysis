"""
Property Fingerprinting Module.

Generates stable identifiers for properties to track listings across time when
listing IDs change. Uses rounded coordinates, quantized area, and stable attributes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pandas as pd


@dataclass(frozen=True)
class FingerprintConfig:
    """
    Configuration for property fingerprint generation.
    
    Attributes:
        lat_round: Decimal places for latitude rounding (default: 4)
        lon_round: Decimal places for longitude rounding (default: 4)
        area_step: Quantization step for area in m² (default: 1.0)
        fingerprint_cols: Additional stable columns to include
        
    Note:
        Rounding reduces sensitivity to coordinate jitter and measurement variance.
    """
    lat_round: int = 4
    lon_round: int = 4
    area_step: float = 1.0

    fingerprint_cols: Tuple[str, ...] = (
        "market",
        "city",
        "listing_type",
        "build_year",
        "floors_total",
        "floor",
        "has_elevator",
        "has_balcony",
        "has_parking_space",
        "has_security",
        "has_storage_room",
    )


def _quantize(series: pd.Series, step: float) -> pd.Series:
    """
    Quantize numeric values to fixed grid.
    
    Args:
        series: Numeric series to quantize
        step: Grid size (must be > 0)
        
    Returns:
        Quantized series aligned to grid
    """
    if step <= 0:
        raise ValueError("area_step must be > 0")
    return (series / step).round(0) * step


def _normalize_for_key(series: pd.Series) -> pd.Series:
    """
    Convert column to deterministic string representation.
    
    Handles missing values with stable tokens:
    - Boolean: False
    - Numeric: -999999
    - Other: "<NA>"
    
    Args:
        series: Column to normalize
        
    Returns:
        String series suitable for fingerprint concatenation
    """
    if pd.api.types.is_bool_dtype(series) or str(series.dtype) == "boolean":
        return series.fillna(False).astype(int).astype(str)

    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(-999999).astype(str)

    return series.fillna("<NA>").astype(str)


def add_property_fingerprint(
    df: pd.DataFrame,
    cfg: FingerprintConfig,
    *,
    lat_col: str = "lat",
    lon_col: str = "lon",
    area_col: str = "area_m2",
    out_col: str = "property_fingerprint",
) -> pd.DataFrame:
    """
    Add a composite fingerprint column to approximate repeated properties across time.
    """
    required = {lat_col, lon_col, area_col}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for fingerprinting: {missing}")

    x = df.copy()

    # Round coordinates to reduce sensitivity to jitter
    x["lat_r"] = x[lat_col].round(cfg.lat_round)
    x["lon_r"] = x[lon_col].round(cfg.lon_round)
    
    # Quantize area to reduce measurement variance
    x["area_q"] = _quantize(x[area_col], cfg.area_step)

    # Build key from stable attributes
    key_cols: list[str] = ["lat_r", "lon_r", "area_q"]
    for c in cfg.fingerprint_cols:
        if c in x.columns:
            key_cols.append(c)

    # Normalize all key columns to strings
    for c in key_cols:
        x[c] = _normalize_for_key(x[c])

    # Concatenate to create fingerprint
    x[out_col] = x[key_cols].agg("|".join, axis=1)

    return x

