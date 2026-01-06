import sys
from pathlib import Path

# Add src/ to Python path to import apartments module
#sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import pytest

from apartments.cleaning import clean_base


def _sample_df():
    return pd.DataFrame(
        {
            "listing_id": [1, 2, 3],
            "city": ["Warszawa", "Warszawa", "Kraków"],
            "listing_type": ["apartment", "apartment", "apartment"],
            "area_m2": [50, 0, 40],                 # one invalid (0)
            "price": [500000, 600000, -10],         # one invalid (-10)
            "month": ["2024-06-01", "2024-06-01", "2024-06-01"],
            "market": ["sale", "sale", "sale"],
            "rooms": ["2", "3", "2"],               # strings -> Int64
            "has_balcony": ["true", "false", "yes"],# strings -> boolean
        }
    )


def test_clean_base_filters_invalid_rows():
    df = _sample_df()
    out = clean_base(df)

    # Only first row is valid (price>0 and area_m2>0)
    assert len(out) == 1
    assert out.iloc[0]["listing_id"] == 1


def test_clean_base_creates_price_per_m2():
    df = _sample_df()
    out = clean_base(df)

    ppm2 = out.iloc[0]["price_per_m2"]
    assert ppm2 == pytest.approx(500000 / 50)


def test_clean_base_coerces_types():
    df = _sample_df()
    out = clean_base(df)

    assert pd.api.types.is_datetime64_any_dtype(out["month"])
    assert str(out["rooms"].dtype) == "Int64"
    assert str(out["has_balcony"].dtype) == "boolean"
    assert pd.api.types.is_float_dtype(out["price_per_m2"])


def test_clean_base_raises_on_missing_required_cols():
    df = pd.DataFrame({"price": [1], "area_m2": [1]})
    with pytest.raises(ValueError):
        clean_base(df)


from apartments.io import load_sale_monthly
sale = load_sale_monthly()
print(sale.columns)
