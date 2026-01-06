from pathlib import Path
import duckdb

import geopandas as gpd
'''
gdf = gpd.read_file("data/reference/warsaw_districts.geojson")
print(len(gdf))
print(gdf["name"].value_counts().head(30))
'''


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    db_path = project_root / "data" / "processed" / "apartments.duckdb"

    if not db_path.exists():
        raise FileNotFoundError(f"DuckDB not found: {db_path}")

    con = duckdb.connect(str(db_path), read_only=True)

    # ---- check schema ----
    print("\n=== TABLE SCHEMA (listings_sale) ===")
    schema = con.execute(
        """
        DESCRIBE listings_sale;
        """
    ).fetchdf()
    print(schema)

    # ---- head of data ----
    print("\n=== HEAD OF DATA (listings_sale) ===")
    head = con.execute(
        """
        SELECT
            month,
            city,
            district,
            listing_type,
            area_m2,
            price,
            price_per_m2
        FROM listings_sale
        ORDER BY month DESC
        LIMIT 10;
        """
    ).fetchdf()

    print(head)

    con.close()


if __name__ == "__main__":
    main()
