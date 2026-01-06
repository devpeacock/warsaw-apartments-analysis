# src/apartments/labels.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


# -------------------------
# Value label mappings (raw -> UI label)
# -------------------------

DISTRICT_LABELS: Dict[str, str] = {
    "praga_północ": "Praga North",
    "praga_południe": "Praga South",
    "śródmieście": "City Centre (Śródmieście)",
    "żoliborz": "Żoliborz",
    "białołęka": "Białołęka",
    "ursynów": "Ursynów",
    "wilanów": "Wilanów",
    "włochy": "Włochy",
    "rembertów": "Rembertów",
    "targówek": "Targówek",
    "bemowo": "Bemowo",
    "bielany": "Bielany",
    "mokotów": "Mokotów",
    "ochota": "Ochota",
    "ursus": "Ursus",
    "wawer": "Wawer",
    "wesoła": "Wesoła",
    "wola": "Wola",
}

LISTING_TYPE_LABELS: Dict[str, str] = {
    "tenement": "Tenement",
    "blockOfFlats": "Block of flats",
    "apartmentBuilding": "Apartment building",
}

CONDITION_LABELS: Dict[str, str] = {
    "low": "Standard",
    "premium": "Premium",
}

OWNERSHIP_LABELS: Dict[str, str] = {
    "condominium": "Condominium",
    "cooperative": "Cooperative",
}

BUILDING_MATERIAL_LABELS: Dict[str, str] = {
    "brick": "Brick",
    "concreteSlab": "Concrete slab",
}


# -------------------------
# Column label mappings (colname -> UI label)
# (optional, for consistent English naming)
# -------------------------

COLUMN_LABELS: Dict[str, str] = {
    "district": "District",
    "price": "Price (PLN)",
    "price_per_m2": "Price per m² (PLN)",
    "area_m2": "Area (m²)",
    "floor": "Floor",
    "floors_total": "Floors total",
    "floor_bin": "Floor (binned)",
    "floors_total_bin": "Total floors (binned)",
    "build_year": "Build year",
    "build_year_bin": "Build year (binned)",
    "listing_type": "Listing type",
    "condition": "Condition",
    "centre_distance": "Distance to centre (max)",
    "ownership": "Ownership",
    "building_material": "Building material",
    "poi_count": "POI count (min)",
    "has_parking_space": "Parking space",
    "has_balcony": "Balcony",
    "has_elevator": "Elevator",
    "has_security": "Security",
    "has_storage_room": "Storage room",
    "school_distance": "School distance (max)",
    "clinic_distance": "Clinic distance (max)",
    "post_office_distance": "Post office distance (max)",
    "kindergarten_distance": "Kindergarten distance (max)",
    "restaurant_distance": "Restaurant distance (max)",
    "college_distance": "College distance (max)",
    "pharmacy_distance": "Pharmacy distance (max)",
}


# -------------------------
# Registry: which mapping belongs to which column
# -------------------------

VALUE_LABELS_BY_COLUMN: Dict[str, Dict[str, str]] = {
    "district": DISTRICT_LABELS,
    "listing_type": LISTING_TYPE_LABELS,
    "condition": CONDITION_LABELS,
    "ownership": OWNERSHIP_LABELS,
    "building_material": BUILDING_MATERIAL_LABELS,
}


# -------------------------
# Helpers
# -------------------------

def label_for_value(column: str, raw_value: str) -> str:
    """raw -> label (fallback to raw if missing)"""
    mapping = VALUE_LABELS_BY_COLUMN.get(column, {})
    return mapping.get(raw_value, str(raw_value))


def build_display_to_raw_map(column: str, raw_values: Iterable[str]) -> Dict[str, str]:
    """
    Build mapping: display_label -> raw_value
    Ensures uniqueness of labels (if collision happens, appends ' [raw]' suffix).
    """
    mapping = VALUE_LABELS_BY_COLUMN.get(column, {})
    disp_to_raw: Dict[str, str] = {}

    for raw in raw_values:
        raw_s = str(raw)
        disp = mapping.get(raw_s, raw_s)

        # Avoid collisions: two raw values might map to same display label
        if disp in disp_to_raw and disp_to_raw[disp] != raw_s:
            disp = f"{disp} [{raw_s}]"

        disp_to_raw[disp] = raw_s

    return disp_to_raw


def column_label(col: str) -> str:
    """colname -> UI label (fallback to a simple title)"""
    return COLUMN_LABELS.get(col, col.replace("_", " ").title())
