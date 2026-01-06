from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pandas as pd


@dataclass(frozen=True)
class FingerprintConfig:
    """
    Configuration for generating a property-level fingerprint used to approximate
    repeated listings across monthly snapshots when listing identifiers are unstable.

    Notes:
    - Coordinates are rounded to reduce sensitivity to minor coordinate jitter.
    - Area is quantized to reduce sensitivity to minor measurement differences.
    - The fingerprint combines multiple stable attributes to reduce false merges.
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
    """Quantize a numeric series to a fixed grid defined by `step`."""
    if step <= 0:
        raise ValueError("area_step must be > 0")
    return (series / step).round(0) * step


def _normalize_for_key(series: pd.Series) -> pd.Series:
    """
    Normalize a column to deterministic strings for fingerprinting.
    Missing values are replaced with stable tokens.
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

    x["lat_r"] = x[lat_col].round(cfg.lat_round)
    x["lon_r"] = x[lon_col].round(cfg.lon_round)
    x["area_q"] = _quantize(x[area_col], cfg.area_step)

    key_cols: list[str] = ["lat_r", "lon_r", "area_q"]
    for c in cfg.fingerprint_cols:
        if c in x.columns:
            key_cols.append(c)

    for c in key_cols:
        x[c] = _normalize_for_key(x[c])

    x[out_col] = x[key_cols].agg("|".join, axis=1)

    return x
