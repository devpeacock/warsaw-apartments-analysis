"""Data loaders for Streamlit dashboard with DuckDB caching."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st


DEFAULT_DB_PATH = Path("data/processed/apartments.duckdb")


def _connect(db_path: str | Path, read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """Open DuckDB connection with read-only mode by default."""
    return duckdb.connect(str(db_path), read_only=read_only)


# ============================================================================
# Static Views (Cross-Month Deduplicated)
# ============================================================================

@st.cache_data(show_spinner=False)
def load_sale_static(db_path: str | Path = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Load deduplicated sale listings from listings_sale_static view. Cached by Streamlit."""
    con = _connect(db_path, read_only=True)
    df = con.execute(
        """
        SELECT *
        FROM listings_sale_static
        """
    ).fetchdf()
    con.close()
    return df


@st.cache_data(show_spinner=False)
def load_rent_static(db_path: str | Path = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Load deduplicated rental listings from listings_rent_static view. Cached by Streamlit."""
    con = _connect(db_path, read_only=True)
    df = con.execute(
        """
        SELECT *
        FROM listings_rent_static
        """
    ).fetchdf()
    con.close()
    return df


# ============================================================================
# Marts (Time Series Aggregations)
# ============================================================================

@st.cache_data(show_spinner=False)
def load_mart_city_month_sale(db_path: str | Path = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Load sale market time series: city-month aggregations. Cached by Streamlit."""
    con = _connect(db_path, read_only=True)
    df = con.execute(
        """
        SELECT *
        FROM mart_city_month_sale
        ORDER BY month
        """
    ).fetchdf()
    con.close()
    return df


@st.cache_data(show_spinner=False)
def load_mart_city_month_rent(db_path: str | Path = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Load rental market time series: city-month aggregations. Cached by Streamlit."""
    con = _connect(db_path, read_only=True)
    df = con.execute(
        """
        SELECT *
        FROM mart_city_month_rent
        ORDER BY month
        """
    ).fetchdf()
    con.close()
    return df


@st.cache_data(show_spinner=False)
def load_mart_city_month_yield_proxy(db_path: str | Path = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Load rental yield proxy time series: city-month aggregations. Cached by Streamlit."""
    con = _connect(db_path, read_only=True)
    df = con.execute(
        """
        SELECT *
        FROM mart_city_month_yield_proxy
        ORDER BY month
        """
    ).fetchdf()
    con.close()
    return df
