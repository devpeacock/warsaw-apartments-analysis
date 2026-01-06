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
    bench = (
        df_sale_static
        .groupby(category)[sale_ppm2_col]
        .median()
        .rename(benchmark_col)
        .reset_index()
    )

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
    Simple aggregated table for yield analysis.
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
