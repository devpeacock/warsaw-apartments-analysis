from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple, Dict, Any

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class FingerprintConfig:
    """
    Configuration for generating a property-level fingerprint used to approximate
    repeated listings across monthly snapshots when listing identifiers are unstable.

    Notes:
    - Latitude/longitude are rounded to reduce sensitivity to minor coordinate jitter.
    - Area is quantized to reduce sensitivity to small measurement/rounding differences.
    - The fingerprint combines multiple stable attributes to avoid collapsing
      multiple distinct units within the same building into a single entity.
    """
    lat_round: int = 4          # ~10–12m at Warsaw latitudes; adjust based on data quality
    lon_round: int = 4
    area_step: float = 1.0      # quantization step in m² (e.g., 1.0, 0.5, 2.0)

    # Candidate features to include in the fingerprint; only those present will be used.
    # Add/remove fields depending on your schema and data quality.
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



@dataclass(frozen=True)
class DuplicateStats:
    """
    Summary statistics describing the prevalence of repeated 'properties' (fingerprints)
    in a long-format dataset assembled from monthly snapshots.
    """
    total_records: int
    total_fingerprints: int

    repeating_fingerprints: int
    repeating_records: int
    repeating_records_share: float

    multi_month_fingerprints: int
    multi_month_records: int
    multi_month_records_share: float


# --------------------------------------------------------------------------------------
# Fingerprint construction
# --------------------------------------------------------------------------------------

def _quantize(series: pd.Series, step: float) -> pd.Series:
    """
    Quantize a numeric series to a fixed grid.
    Example: step=1.0 converts 49.9 -> 50.0, 50.1 -> 50.0 (depending on rounding).
    """
    if step <= 0:
        raise ValueError("area_step must be > 0")
    return (series / step).round(0) * step


def _normalize_for_key(series: pd.Series) -> pd.Series:
    """
    Normalize a column for deterministic string-based fingerprinting.
    Missing values are replaced with stable tokens to avoid producing NaN keys.
    """
    if pd.api.types.is_bool_dtype(series) or str(series.dtype) == "boolean":
        # Treat missing booleans as False for fingerprinting purposes.
        return series.fillna(False).astype(int).astype(str)

    if pd.api.types.is_numeric_dtype(series):
        # Use a numeric sentinel that is unlikely to collide with valid values.
        return series.fillna(-999999).astype(str)

    # Treat everything else as string-like.
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

    The fingerprint includes rounded coordinates and quantized area, plus a set of
    additional stable attributes (when available) to reduce false merges.
    """
    required = {lat_col, lon_col, area_col}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for fingerprinting: {missing}")

    x = df.copy()

    # Coordinate rounding to reduce sensitivity to small location noise.
    x["lat_r"] = x[lat_col].round(cfg.lat_round)
    x["lon_r"] = x[lon_col].round(cfg.lon_round)

    # Area quantization to reduce sensitivity to minor measurement/rounding differences.
    x["area_q"] = _quantize(x[area_col], cfg.area_step)

    # Assemble the set of fingerprint components that actually exist in the dataset.
    key_cols: list[str] = ["lat_r", "lon_r", "area_q"]
    for c in cfg.fingerprint_cols:
        if c in x.columns:
            key_cols.append(c)

    # Normalize each component into a deterministic string representation.
    for c in key_cols:
        x[c] = _normalize_for_key(x[c])

    # Join components into a single fingerprint string.
    x[out_col] = x[key_cols].agg("|".join, axis=1)

    return x


# --------------------------------------------------------------------------------------
# Duplicate / repeat prevalence metrics
# --------------------------------------------------------------------------------------

def compute_repeat_stats(
    df: pd.DataFrame,
    *,
    fingerprint_col: str = "property_fingerprint",
    month_col: str = "month",
    top_n: int = 20,
) -> Tuple[DuplicateStats, pd.DataFrame]:
    """
    Compute prevalence metrics for repeated 'properties' using the fingerprint.

    Returns:
    - DuplicateStats: high-level summary
    - top_groups: top repeating fingerprints by (n_months, n_records)
    """
    required = {fingerprint_col, month_col}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for repeat stats: {missing}")

    grp = (
        df.groupby(fingerprint_col, as_index=False)
        .agg(
            n_records=(fingerprint_col, "size"),
            n_months=(month_col, "nunique"),
            min_month=(month_col, "min"),
            max_month=(month_col, "max"),
        )
    )

    total_records = int(len(df))
    total_fingerprints = int(len(grp))

    repeating_mask = grp["n_records"] > 1
    repeating_fingerprints = int(repeating_mask.sum())
    repeating_records = int(grp.loc[repeating_mask, "n_records"].sum())
    repeating_share = float(repeating_records / total_records) if total_records else 0.0

    multi_month_mask = grp["n_months"] > 1
    multi_month_fingerprints = int(multi_month_mask.sum())
    multi_month_records = int(grp.loc[multi_month_mask, "n_records"].sum())
    multi_month_share = float(multi_month_records / total_records) if total_records else 0.0

    stats = DuplicateStats(
        total_records=total_records,
        total_fingerprints=total_fingerprints,
        repeating_fingerprints=repeating_fingerprints,
        repeating_records=repeating_records,
        repeating_records_share=repeating_share,
        multi_month_fingerprints=multi_month_fingerprints,
        multi_month_records=multi_month_records,
        multi_month_records_share=multi_month_share,
    )

    top_groups = (
        grp.sort_values(["n_months", "n_records"], ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    return stats, top_groups


# --------------------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------------------

def load_parquet_filtered(path: Path) -> pd.DataFrame:
    """
    Load a parquet dataset and apply minimal validity filtering required for fingerprinting.

    The filter is intentionally conservative; substantive outlier handling should remain
    in the analysis layer.
    """
    df = pd.read_parquet(path)

    # Minimal filtering for fingerprint robustness.
    for col in ("lat", "lon", "area_m2", "price", "month"):
        if col not in df.columns:
            raise ValueError(f"Required column missing from parquet: {col}")

    df = df.dropna(subset=["lat", "lon", "area_m2", "price", "month"])
    df = df[(df["area_m2"] > 0) & (df["price"] > 0)]

    return df


def run_repeat_prevalence(
    parquet_path: Path,
    cfg: FingerprintConfig,
    *,
    top_n: int = 20,
) -> Tuple[DuplicateStats, pd.DataFrame]:
    """
    Load a processed parquet file, generate fingerprints, and compute repeat prevalence.
    """
    df = load_parquet_filtered(parquet_path)
    df = add_property_fingerprint(df, cfg)
    stats, top_groups = compute_repeat_stats(df, top_n=top_n)

    print(f"\n=== {parquet_path.name} ===")
    print(
        "records:", stats.total_records,
        "| unique_fingerprints:", stats.total_fingerprints,
        "| repeating_fingerprints:", stats.repeating_fingerprints,
        "| repeating_records_share:", f"{stats.repeating_records_share:.2%}",
        "| multi_month_fingerprints:", stats.multi_month_fingerprints,
        "| multi_month_records_share:", f"{stats.multi_month_records_share:.2%}",
    )
    print("\nTop repeating fingerprints:")
    print(top_groups.to_string(index=False))

    return stats, top_groups


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    processed_dir = project_root / "data" / "processed"

    sale_path = processed_dir / "sale_long.parquet"
    rent_path = processed_dir / "rent_long.parquet"

    # Tune these parameters based on observed coordinate noise and area consistency.
    cfg = FingerprintConfig(
        lat_round=4,
        lon_round=4,
        area_step=1.0,
        fingerprint_cols=FingerprintConfig.fingerprint_cols,
    )

    run_repeat_prevalence(sale_path, cfg, top_n=20)
    run_repeat_prevalence(rent_path, cfg, top_n=20)
