# scripts/build_db.py
from pathlib import Path
import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"

DB_PATH = PROCESSED / "apartments.duckdb"
SALE_PARQUET = PROCESSED / "sale_long.parquet"
RENT_PARQUET = PROCESSED / "rent_long.parquet"

# Integer columns that should be cast to INTEGER type
INT_COLS = ["rooms", "floor", "floors_total", "build_year"]


def _create_int_cast_sql(cols: list[str]) -> str:
    """Generate SQL to cast integer columns, filtering sentinel values."""
    cast_clauses = ",\n            ".join(
        # Try to cast to DOUBLE first, then filter sentinel values, then cast to INTEGER
        f"CASE WHEN TRY_CAST({col} AS DOUBLE) != -999999.0 THEN CAST(TRY_CAST({col} AS DOUBLE) AS INTEGER) ELSE NULL END AS {col}_int"
        for col in cols
    )
    return f",\n            {cast_clauses}"


def _drop_and_rename_int_cols(con: duckdb.DuckDBPyConnection, table: str, cols: list[str]) -> None:
    """Drop original columns and rename _int versions back to original names."""
    for col in cols:
        con.execute(f"ALTER TABLE {table} DROP {col};")
    for col in cols:
        con.execute(f"ALTER TABLE {table} RENAME {col}_int TO {col};")


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))
    con.execute("PRAGMA threads=4;")
    con.execute("PRAGMA enable_progress_bar=true;")

    # 1) Base tables
    con.execute("DROP TABLE IF EXISTS listings_sale;")
    con.execute("DROP TABLE IF EXISTS listings_rent;")

    # Generate dynamic CAST clauses for integer columns
    int_cast_sql = _create_int_cast_sql(INT_COLS)

    con.execute(
        f"""
        CREATE TABLE listings_sale AS
        SELECT 
            *{int_cast_sql}
        FROM read_parquet(?)
        WHERE true;
        """,
        [str(SALE_PARQUET)],
    )
    
    _drop_and_rename_int_cols(con, "listings_sale", INT_COLS)
    
    con.execute(
        f"""
        CREATE TABLE listings_rent AS
        SELECT 
            *{int_cast_sql}
        FROM read_parquet(?)
        WHERE true;
        """,
        [str(RENT_PARQUET)],
    )
    
    _drop_and_rename_int_cols(con, "listings_rent", INT_COLS)

    # 2) Helpful views
    con.execute("DROP VIEW IF EXISTS listings_all;")
    con.execute(
        """
        CREATE VIEW listings_all AS
        SELECT * FROM listings_sale
        UNION ALL
        SELECT * FROM listings_rent;
        """
    )

        # 2b) Static analysis views: one row per property_fingerprint (dedup across months)
    con.execute("DROP VIEW IF EXISTS listings_sale_static;")
    con.execute(
        """
        CREATE VIEW listings_sale_static AS
        SELECT * EXCLUDE (rn)
        FROM (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY property_fingerprint
                    ORDER BY month DESC, price DESC
                ) AS rn
            FROM listings_sale
            WHERE property_fingerprint IS NOT NULL
        )
        WHERE rn = 1;
        """
    )

    con.execute("DROP VIEW IF EXISTS listings_rent_static;")
    con.execute(
        """
        CREATE VIEW listings_rent_static AS
        SELECT * EXCLUDE (rn)
        FROM (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY property_fingerprint
                    ORDER BY month DESC, price DESC
                ) AS rn
            FROM listings_rent
            WHERE property_fingerprint IS NOT NULL
        )
        WHERE rn = 1;
        """
    )
    # 2c) Combined static view - sale + rent
    con.execute("DROP VIEW IF EXISTS listings_static_all;")
    con.execute(
        """
        CREATE VIEW listings_static_all AS
        SELECT * FROM listings_sale_static
        UNION ALL
        SELECT * FROM listings_rent_static;
        """
    )


    # 3) Simple QA checks (fail fast would be nicer, but minimum sanity here)
    qa = con.execute(
        """
        SELECT market, COUNT(*) AS n,
               SUM(price <= 0) AS bad_price,
               SUM(area_m2 <= 0) AS bad_area,
               SUM(price_per_m2 IS NULL) AS null_ppm2
        FROM listings_all
        GROUP BY 1
        ORDER BY 1;
        """
    ).fetchall()
    print("QA:", qa)

    # 4) Create marts as views (you can materialize later)
    # City-month: sale
    con.execute("DROP VIEW IF EXISTS mart_city_month_sale;")
    con.execute(
        """
        CREATE VIEW mart_city_month_sale AS
        SELECT
            month,
            city,
            COUNT(*) AS n_listings,
            quantile_cont(price_per_m2, 0.5) AS median_ppm2,
            quantile_cont(price_per_m2, 0.25) AS p25_ppm2,
            quantile_cont(price_per_m2, 0.75) AS p75_ppm2,
            AVG(price_per_m2) AS avg_ppm2
        FROM listings_sale
        GROUP BY 1,2;
        """
    )

    # City-month: rent
    con.execute("DROP VIEW IF EXISTS mart_city_month_rent;")
    con.execute(
        """
        CREATE VIEW mart_city_month_rent AS
        SELECT
            month,
            city,
            COUNT(*) AS n_listings,
            quantile_cont(price_per_m2, 0.5) AS median_ppm2,
            quantile_cont(price_per_m2, 0.25) AS p25_ppm2,
            quantile_cont(price_per_m2, 0.75) AS p75_ppm2,
            AVG(price_per_m2) AS avg_ppm2
        FROM listings_rent
        GROUP BY 1,2;
        """
    )

    # Yield proxy: rent median / sale median (monthly rent per m2 vs sale price per m2)
    con.execute("DROP VIEW IF EXISTS mart_city_month_yield_proxy;")
    con.execute(
        """
        CREATE VIEW mart_city_month_yield_proxy AS
        SELECT
            s.month,
            s.city,
            s.n_listings AS n_sale,
            r.n_listings AS n_rent,
            s.median_ppm2 AS sale_median_ppm2,
            r.median_ppm2 AS rent_median_ppm2,
            (r.median_ppm2 * 12.0) / NULLIF(s.median_ppm2, 0) AS gross_yield_proxy
        FROM mart_city_month_sale s
        JOIN mart_city_month_rent r
          ON s.month = r.month
         AND s.city = r.city;
        """
    )

    con.close()
    print(f"Built DuckDB at: {DB_PATH}")


if __name__ == "__main__":
    main()
