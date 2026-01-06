from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import pandas as pd

from apartments.fingerprint import FingerprintConfig, add_property_fingerprint


@dataclass(frozen=True)
class DuplicateStats:
    """
    Summary statistics describing the prevalence of repeated 'properties'
    (fingerprints) in a long-format dataset assembled from monthly snapshots.
    """
    total_records: int
    total_fingerprints: int
    repeating_fingerprints: int
    repeating_records_share: float
    multi_month_fingerprints: int
    multi_month_records_share: float


def compute_repeat_stats(
    df: pd.DataFrame,
    *,
    fingerprint_col: str = "property_fingerprint",
    month_col: str = "month",
    top_n: int = 20,
) -> Tuple[DuplicateStats, pd.DataFrame]:
    """Compute repeat prevalence metrics and return summary + top groups."""
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

    repeating_share = float(grp.loc[grp["n_records"] > 1, "n_records"].sum() / total_records) if total_records else 0.0
    multi_month_share = float(grp.loc[grp["n_months"] > 1, "n_records"].sum() / total_records) if total_records else 0.0

    stats = DuplicateStats(
        total_records=total_records,
        total_fingerprints=total_fingerprints,
        repeating_fingerprints=int((grp["n_records"] > 1).sum()),
        repeating_records_share=repeating_share,
        multi_month_fingerprints=int((grp["n_months"] > 1).sum()),
        multi_month_records_share=multi_month_share,
    )

    top_groups = (
        grp.sort_values(["n_months", "n_records"], ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    return stats, top_groups


def load_parquet_filtered(path: Path) -> pd.DataFrame:
    """Load parquet and apply minimal filtering required for fingerprinting."""
    df = pd.read_parquet(path)
    df = df.dropna(subset=["lat", "lon", "area_m2", "price", "month"])
    df = df[(df["area_m2"] > 0) & (df["price"] > 0)]
    return df


def run_repeat_prevalence(parquet_path: Path, cfg: FingerprintConfig, *, top_n: int = 20) -> None:
    """Run repeat prevalence diagnostics for a given dataset."""
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


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    processed_dir = project_root / "data" / "processed"

    sale_path = processed_dir / "sale_long.parquet"
    rent_path = processed_dir / "rent_long.parquet"

    cfg = FingerprintConfig(lat_round=4, lon_round=4, area_step=1.0)

    run_repeat_prevalence(sale_path, cfg, top_n=20)
    run_repeat_prevalence(rent_path, cfg, top_n=20)
