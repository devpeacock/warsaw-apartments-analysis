# streamlit_app/components/sidebar.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Add src/ to Python path for apartments package
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pandas as pd
import streamlit as st

from apartments.labels import build_display_to_raw_map, column_label

# components/sidebar.py

def _sidebar_title(text: str):
    st.sidebar.markdown(f'<div class="sidebar-title">{text}</div>', unsafe_allow_html=True)

def _sidebar_section_start(label: str):
    st.sidebar.markdown(
        f"""
        <div class="sidebar-card">
          <div class="sidebar-section-label">
            <span>{label}</span>
          </div>
        """,
        unsafe_allow_html=True,
    )

def _sidebar_section_end():
    st.sidebar.markdown("</div>", unsafe_allow_html=True)



def _safe_numeric_series(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce").dropna()


def _q_range(df: pd.DataFrame, col: str, qlo: float = 0.01, qhi: float = 0.99) -> Tuple[float, float]:
    s = _safe_numeric_series(df, col)
    if s.empty:
        return 0.0, 1.0
    lo = float(s.quantile(qlo))
    hi = float(s.quantile(qhi))
    if not (hi > lo):
        hi = lo + 1.0
    return lo, hi


def _multiselect_mapped(df: pd.DataFrame, col: str, *, label: str) -> Any:
    if col not in df.columns:
        return None
    raw_values = sorted([x for x in df[col].dropna().unique()])
    if not raw_values:
        return None

    disp_to_raw = build_display_to_raw_map(col, raw_values)
    selected_disp = st.sidebar.multiselect(label, list(disp_to_raw.keys()), default=[])

    if not selected_disp:
        return None
    return [disp_to_raw[d] for d in selected_disp]


def _range_slider(df: pd.DataFrame, col: str, *, label: str, default: Optional[Tuple[float, float]] = None) -> Optional[Tuple[float, float]]:
    if col not in df.columns:
        return None
    lo, hi = _q_range(df, col, 0.01, 0.99)
    if default is None:
        default = (lo, hi)
    return st.sidebar.slider(label, min_value=float(lo), max_value=float(hi), value=(float(default[0]), float(default[1])))


def _minmax_int_inputs(df: pd.DataFrame, col: str, *, label: str) -> Optional[Tuple[int | None, int | None]]:
    if col not in df.columns:
        return None

    s = _safe_numeric_series(df, col)
    if s.empty:
        return (None, None)

    lo_q = int(s.quantile(0.01))
    hi_q = int(s.quantile(0.99))
    lo_min = int(s.min())
    hi_max = int(s.max())

    lo_default = max(lo_min, lo_q)
    hi_default = min(hi_max, hi_q)

    st.sidebar.markdown(f"**{label}**")
    c1, c2 = st.sidebar.columns(2)

    with c1:
        vmin = st.number_input("Min", min_value=lo_min, max_value=hi_max, value=lo_default, step=1, key=f"{col}_min")
    with c2:
        vmax = st.number_input("Max", min_value=lo_min, max_value=hi_max, value=hi_default, step=1, key=f"{col}_max")

    if vmin > vmax:
        vmin, vmax = vmax, vmin

    return (int(vmin), int(vmax))


def _max_only_slider(df: pd.DataFrame, col: str, *, label: str) -> Optional[Tuple[None, float]]:
    if col not in df.columns:
        return None
    lo, hi = _q_range(df, col, 0.01, 0.99)
    vmax = st.sidebar.slider(label, min_value=max(0.0, float(lo)), max_value=float(hi), value=float(hi))
    return (None, float(vmax))


def _min_only_slider_int(df: pd.DataFrame, col: str, *, label: str) -> Optional[Tuple[int, None]]:
    if col not in df.columns:
        return None
    s = _safe_numeric_series(df, col)
    if s.empty:
        return (0, None)

    min_val = int(max(0, s.min()))
    max_val = int(s.max())
    default = int(max(0, s.quantile(0.01)))

    vmin = st.sidebar.slider(label, min_value=min_val, max_value=max_val, value=default, step=1)
    return (int(vmin), None)


def render_sidebar(df_base: pd.DataFrame, *, title: str = "Filters") -> Dict[str, Any]:
    st.sidebar.title(title)
    filters: Dict[str, Any] = {}

    # Section 1: Location
    _sidebar_section_start("Location")
    # 1) District (top)
    filters["district"] = _multiselect_mapped(df_base, "district", label=column_label("district"))
    _sidebar_section_end()

    # Section 2: Price & Area
    _sidebar_section_start("Price & Area")
    # 2) Price
    filters["price"] = _range_slider(df_base, "price", label=column_label("price"))

    # 3) Price per m2
    filters["price_per_m2"] = _range_slider(df_base, "price_per_m2", label=column_label("price_per_m2"))

    # 4) Area (full range by default)
    if "area_m2" in df_base.columns:
        filters["area_m2"] = _range_slider(df_base, "area_m2", label=column_label("area_m2"))
    _sidebar_section_end()

    # Section 3: Building
    _sidebar_section_start("Building")
    # 5) Floor (min/max)
    v = _minmax_int_inputs(df_base, "floor", label=column_label("floor"))
    if v is not None:
        filters["floor"] = v

    # 6) Floors total (min/max)
    v = _minmax_int_inputs(df_base, "floors_total", label=column_label("floors_total"))
    if v is not None:
        filters["floors_total"] = v

    # 7) Build year (min/max)
    v = _minmax_int_inputs(df_base, "build_year", label=column_label("build_year"))
    if v is not None:
        filters["build_year"] = v
    _sidebar_section_end()

    # Section 4: Property
    _sidebar_section_start("Property")
    # 8) Listing type
    filters["listing_type"] = _multiselect_mapped(df_base, "listing_type", label=column_label("listing_type"))

    # 9) Condition
    filters["condition"] = _multiselect_mapped(df_base, "condition", label=column_label("condition"))

    # 10) Centre distance (max-only)
    v = _max_only_slider(df_base, "centre_distance", label=column_label("centre_distance"))
    if v is not None:
        filters["centre_distance"] = v

    # 11) Ownership
    filters["ownership"] = _multiselect_mapped(df_base, "ownership", label=column_label("ownership"))

    # 12) Building material
    filters["building_material"] = _multiselect_mapped(df_base, "building_material", label=column_label("building_material"))

    # 13) POI count (min-only int)
    v = _min_only_slider_int(df_base, "poi_count", label=column_label("poi_count"))
    if v is not None:
        filters["poi_count"] = v
    _sidebar_section_end()

    # Section 5: Amenities
    _sidebar_section_start("Amenities")
    # 14) Amenities (checkboxes)
    for col in ["has_parking_space", "has_balcony", "has_elevator", "has_security", "has_storage_room"]:
        if col in df_base.columns:
            checked = st.sidebar.checkbox(column_label(col), value=False, key=f"chk_{col}")
            filters[col] = True if checked else None
    _sidebar_section_end()

    # Section 6: Distances
    _sidebar_section_start("Distances")
    # 15) Distances (max-only sliders)
    for col in [
        "school_distance",
        "clinic_distance",
        "post_office_distance",
        "kindergarten_distance",
        "restaurant_distance",
        "college_distance",
        "pharmacy_distance",
    ]:
        v = _max_only_slider(df_base, col, label=column_label(col))
        if v is not None:
            filters[col] = v
    _sidebar_section_end()

    st.sidebar.divider()

    clip = st.sidebar.toggle("Clip outliers (P1–P99)", value=True)
    filters["_clip"] = clip

    # cleanup
    cleaned: Dict[str, Any] = {}
    for k, v in filters.items():
        if v is None:
            continue
        if isinstance(v, list) and len(v) == 0:
            continue
        cleaned[k] = v

    return cleaned
