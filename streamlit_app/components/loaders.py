# streamlit_app/components/loaders.py
from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st


DEFAULT_DB_PATH = Path("data/processed/apartments.duckdb")


def _connect(db_path: str | Path, read_only: bool = True) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(db_path), read_only=read_only)


# -------------------------
# Static views (cross-month dedup)
# -------------------------

@st.cache_data(show_spinner=False)
def load_sale_static(db_path: str | Path = DEFAULT_DB_PATH) -> pd.DataFrame:
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
    con = _connect(db_path, read_only=True)
    df = con.execute(
        """
        SELECT *
        FROM listings_rent_static
        """
    ).fetchdf()
    con.close()
    return df


# -------------------------
# Marts (time series)
# -------------------------

@st.cache_data(show_spinner=False)
def load_mart_city_month_sale(db_path: str | Path = DEFAULT_DB_PATH) -> pd.DataFrame:
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
