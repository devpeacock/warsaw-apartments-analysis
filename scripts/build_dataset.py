"""Build clean long-format datasets from raw monthly apartment listings.

Loads raw sale and rent data, applies cleaning pipeline, and saves processed
parquet files to data/processed/. Run this script whenever raw data is updated.
"""

from apartments.io import load_sale_monthly, load_rent_monthly
from apartments.cleaning import clean_base
from apartments.io import save_processed


# ============================================================================
# Main Processing
# ============================================================================

def main():
    """Load raw data, clean it, and save processed datasets to parquet files."""
    sale = clean_base(load_sale_monthly())
    rent = clean_base(load_rent_monthly())

    sale_path = save_processed(sale, "sale_long")
    rent_path = save_processed(rent, "rent_long")

    print("Saved:")
    print(" -", sale_path)
    print(" -", rent_path)
    print("Rows:", {"sale": len(sale), "rent": len(rent)})


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    main()
