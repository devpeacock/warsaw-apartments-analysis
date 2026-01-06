import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apartments.io import load_sale_monthly, load_rent_monthly

sale = load_sale_monthly()
rent = load_rent_monthly()

print("SALE shape:", sale.shape)
print("RENT shape:", rent.shape)

sale.head()

expected_cols = {
    "listing_id",
    "city",
    "listing_type",
    "area_m2",
    "rooms",
    "floor",
    "floors_total",
    "build_year",
    "lat",
    "lon",
    "centre_distance",
    "poi_count",
    "school_distance",
    "clinic_distance",
    "post_office_distance",
    "kindergarten_distance",
    "restaurant_distance",
    "college_distance",
    "pharmacy_distance",
    "ownership",
    "building_material",
    "condition",
    "has_parking_space",
    "has_balcony",
    "has_elevator",
    "has_security",
    "has_storage_room",
    "price",
    "month",
    "market",
}

missing = expected_cols - set(sale.columns)
print("Missing columns:", missing)

print(sale["month"].dtype, sale["month"].min(), sale["month"].max())

print(sale["month"].value_counts().sort_index())

print(sale["market"].unique(), rent["market"].unique())