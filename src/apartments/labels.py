"""
Display Labels and Mappings Module.

Provides human-readable labels for categorical values and column names in the UI.
Maps internal data values to user-friendly display text in English and Polish.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


# ============================================================================
# Value Label Mappings (Raw Value -> UI Label)
# ============================================================================

# Warsaw district names with Polish characters preserved
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

# Property type categories
LISTING_TYPE_LABELS: Dict[str, str] = {
    "tenement": "Tenement",
    "blockOfFlats": "Block of flats",
    "apartmentBuilding": "Apartment building",
}

# Apartment condition quality levels
CONDITION_LABELS: Dict[str, str] = {
    "low": "Standard",
    "premium": "Premium",
}

# Ownership types in Polish housing market
OWNERSHIP_LABELS: Dict[str, str] = {
    "condominium": "Condominium",
    "cooperative": "Cooperative",
}

# Building construction material types
BUILDING_MATERIAL_LABELS: Dict[str, str] = {
    "brick": "Brick",
    "concreteSlab": "Concrete slab",
}


# ============================================================================
# Column Label Mappings (Column Name -> UI Label)
# ============================================================================

# Maps internal column names to display-friendly English labels
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


# ============================================================================
# Column-to-Mapping Registry
# ============================================================================

# Maps column names to their respective value label dictionaries
VALUE_LABELS_BY_COLUMN: Dict[str, Dict[str, str]] = {
    "district": DISTRICT_LABELS,
    "listing_type": LISTING_TYPE_LABELS,
    "condition": CONDITION_LABELS,
    "ownership": OWNERSHIP_LABELS,
    "building_material": BUILDING_MATERIAL_LABELS,
}


# ============================================================================
# Label Helper Functions
# ============================================================================

def label_for_value(column: str, raw_value: str) -> str:
    """
    Get display label for a raw categorical value.
    
    Args:
        column: Column name (e.g., 'district', 'listing_type')
        raw_value: Raw value from data (e.g., 'mokotów', 'tenement')
        
    Returns:
        Display label if mapping exists, otherwise raw value as string
        
    Example:
        >>> label_for_value('district', 'mokotów')
        'Mokotów'
    """
    mapping = VALUE_LABELS_BY_COLUMN.get(column, {})
    return mapping.get(raw_value, str(raw_value))


def build_display_to_raw_map(column: str, raw_values: Iterable[str]) -> Dict[str, str]:
    """
    Build reverse mapping from display labels to raw values.
    
    Handles collisions by appending '[raw_value]' suffix when multiple
    raw values map to the same display label.
    
    Args:
        column: Column name to get mapping for
        raw_values: Iterable of raw values present in data
        
    Returns:
        Dict mapping display labels to raw values
        
    Example:
        >>> build_display_to_raw_map('district', ['mokotów', 'wola'])
        {'Mokotów': 'mokotów', 'Wola': 'wola'}
    """
    mapping = VALUE_LABELS_BY_COLUMN.get(column, {})
    disp_to_raw: Dict[str, str] = {}

    for raw in raw_values:
        raw_s = str(raw)
        disp = mapping.get(raw_s, raw_s)

        # Avoid collisions: add suffix if display label already used
        if disp in disp_to_raw and disp_to_raw[disp] != raw_s:
            disp = f"{disp} [{raw_s}]"

        disp_to_raw[disp] = raw_s

    return disp_to_raw


def column_label(col: str) -> str:
    """
    Get display label for a column name.
    
    Args:
        col: Internal column name (e.g., 'price_per_m2')
        
    Returns:
        Display label if mapping exists, otherwise title-cased column name
        
    Example:
        >>> column_label('price_per_m2')
        'Price per m² (PLN)'
    """
    return COLUMN_LABELS.get(col, col.replace("_", " ").title())
