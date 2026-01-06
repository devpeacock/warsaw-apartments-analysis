"""
Rental Yield Calculation Module.

Computes gross rental yield estimates by comparing monthly rental prices
to sale prices aggregated by categorical segments (e.g., district, property type).
"""

import pandas as pd


def make_yield_df(
    df_sale_static: pd.DataFrame,
    df_rent: pd.DataFrame,
    category: str,
    *,
    rent_ppm2_col: str = "price_per_m2",
    sale_ppm2_col: str = "price_per_m2",
    annualization: float = 12.0,
    yield_col: str = "gross_yield_pct",
    benchmark_col: str = "sale_ppm2_benchmark",
) -> pd.DataFrame:
    """
    Create a rent-level yield proxy using a SALE benchmark aggregated by `category`.

    For each rent listing:
        yield_pct = (rent_ppm2 * annualization / median(sale_ppm2 | category)) * 100
    """
    # Compute median sale price per m² benchmark for each category
    bench = (
        df_sale_static
        .groupby(category)[sale_ppm2_col]
        .median()
        .rename(benchmark_col)
        .reset_index()
    )

    # Merge benchmark with rental data and calculate yield
    out = df_rent.merge(bench, on=category, how="inner")
    out[yield_col] = (out[rent_ppm2_col] * annualization / out[benchmark_col]) * 100
    return out


def yield_summary(
    df_yield: pd.DataFrame,
    group_col: str,
    *,
    yield_col: str = "gross_yield_pct",
) -> pd.DataFrame:
    """
    Aggregate rental yield statistics by group.
    
    Computes count, median, quartiles, and mean of yield percentages
    for each group, sorted by median yield descending.
    
    Args:
        df_yield: DataFrame with yield calculations
        group_col: Column name to group by (e.g., 'district', 'listing_type')
        yield_col: Column name containing yield percentages (default: 'gross_yield_pct')
        
    Returns:
        DataFrame with columns: n (count), median, p25, p75, mean
        Indexed by group_col, sorted by median descending
        
    Example:
        >>> summary = yield_summary(yield_df, group_col='district')
        >>> summary.head()
                     n  median    p25    p75   mean
        district                                    
        mokotów    150    5.2   4.8    5.6    5.3
    """
    return (
        df_yield
        .groupby(group_col)[yield_col]
        .agg(
            n="count",
            median="median",
            p25=lambda x: x.quantile(0.25),
            p75=lambda x: x.quantile(0.75),
            mean="mean",
        )
        .sort_values("median", ascending=False)
    )
