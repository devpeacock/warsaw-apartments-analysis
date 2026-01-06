"""Visualization and filtering tools for apartment data analysis with Plotly dashboards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd

from apartments.labels import label_for_value, column_label


Number = Union[int, float]
Range = Tuple[Optional[Number], Optional[Number]]

# Columns that display as years (skip compact formatting)
YEAR_COLUMNS = {"build_year", "year", "construction_year"}


# ============================================================================
# Filter System
# ============================================================================

@dataclass(frozen=True)
class FilterSpec:
    """Declarative filter: column, kind (in_enum/range/bool_true), and allowed values for categorical."""
    column: str
    kind: str
    allowed: Optional[Sequence[str]] = None


# Valid categorical values for filter validation
ALLOWED: Dict[str, Sequence[str]] = {
    "listing_type": ("tenement", "blockOfFlats", "apartmentBuilding"),
    "ownership": ("condominium", "cooperative"),
    "building_material": ("brick", "concreteSlab"),
    "condition": ("low", "premium"),
    "district": (
        "praga_północ",
        "śródmieście",
        "wola",
        "bemowo",
        "żoliborz",
        "rembertów",
        "praga_południe",
        "bielany",
        "targówek",
        "białołęka",
        "ursynów",
        "wilanów",
        "wawer",
        "mokotów",
        "włochy",
        "ursus",
        "ochota",
        "wesoła",
    ),
}


# --------------------------------------------------------------------------------------
# Filter registry: add new filters here
# --------------------------------------------------------------------------------------

FILTERS: Dict[str, FilterSpec] = {
    # Categoricals (validated)
    "district": FilterSpec("district", "in_enum", allowed=ALLOWED["district"]),
    "listing_type": FilterSpec("listing_type", "in_enum", allowed=ALLOWED["listing_type"]),
    "ownership": FilterSpec("ownership", "in_enum", allowed=ALLOWED["ownership"]),
    "building_material": FilterSpec("building_material", "in_enum", allowed=ALLOWED["building_material"]),
    "condition": FilterSpec("condition", "in_enum", allowed=ALLOWED["condition"]),

    # Numeric ranges
    "area_m2": FilterSpec("area_m2", "range"),
    "price": FilterSpec("price", "range"),
    "price_per_m2": FilterSpec("price_per_m2", "range"),
    "rooms": FilterSpec("rooms", "range"),
    "floor": FilterSpec("floor", "range"),
    "floors_total": FilterSpec("floors_total", "range"),
    "poi_count": FilterSpec("poi_count", "range"),
    "build_year": FilterSpec("build_year", "range"),

    # Distances (optional)
    "centre_distance": FilterSpec("centre_distance", "range"),
    "school_distance": FilterSpec("school_distance", "range"),
    "clinic_distance": FilterSpec("clinic_distance", "range"),
    "post_office_distance": FilterSpec("post_office_distance", "range"),
    "kindergarten_distance": FilterSpec("kindergarten_distance", "range"),
    "restaurant_distance": FilterSpec("restaurant_distance", "range"),
    "college_distance": FilterSpec("college_distance", "range"),
    "pharmacy_distance": FilterSpec("pharmacy_distance", "range"),

    # Boolean flags (keep only True)
    "has_parking_space": FilterSpec("has_parking_space", "bool_true"),
    "has_balcony": FilterSpec("has_balcony", "bool_true"),
    "has_elevator": FilterSpec("has_elevator", "bool_true"),
    "has_security": FilterSpec("has_security", "bool_true"),
    "has_storage_room": FilterSpec("has_storage_room", "bool_true"),
}


def _as_list(value: Any) -> list[Any]:
    """Convert value to list, handling None, sequences, and scalars."""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def apply_filters(df: pd.DataFrame, spec: Dict[str, Any]) -> pd.DataFrame:
    """Apply filters from spec dict: in_enum uses isin(), range clips min/max, bool_true keeps truthy values. Validates categorical values against ALLOWED."""
    out = df

    for name, value in spec.items():
        f = FILTERS.get(name)
        if f is None:
            continue

        if value is None:
            continue

        if f.column not in out.columns:
            continue

        if f.kind == "in_enum":
            values = _as_list(value)
            if len(values) == 0:
                continue

            allowed = set(f.allowed or [])
            invalid = [v for v in values if v not in allowed]
            if invalid:
                raise ValueError(
                    f"Invalid value(s) for '{name}': {invalid}. "
                    f"Allowed: {sorted(allowed)}"
                )

            out = out[out[f.column].isin(values)]

        elif f.kind == "range":
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ValueError(f"Range filter '{name}' expects (min, max), got: {value}")

            lo, hi = value
            if lo is not None:
                out = out[out[f.column] >= lo]
            if hi is not None:
                out = out[out[f.column] <= hi]

        elif f.kind == "bool_true":
            if bool(value):
                # Handle both boolean True and string '1' from DuckDB
                out = out[out[f.column].isin([True, 1, '1', 'true', 'True'])]

        else:
            raise ValueError(f"Unknown filter kind: {f.kind}")

    return out.copy()


# ============================================================================
# Data Clipping Utilities
# ============================================================================

import matplotlib.pyplot as plt


def get_clip_bounds(
    df: pd.DataFrame,
    cols: Sequence[str],
    *,
    clip: bool = True,
    p_low: float = 0.01,
    p_high: float = 0.99,
) -> Dict[str, Tuple[float, float]]:
    """Compute (p_low, p_high) percentile bounds for each column to clip outliers. Returns dict of {col: (lower, upper)}."""
    if not clip or len(cols) == 0:
        return {}

    bounds: Dict[str, Tuple[float, float]] = {}
    for c in cols:
        if c not in df.columns:
            continue
        s = pd.to_numeric(df[c], errors="coerce").dropna()
        if s.empty:
            continue
        bounds[c] = (float(s.quantile(p_low)), float(s.quantile(p_high)))
    return bounds


def clip_series(s: pd.Series, bounds: Optional[Tuple[float, float]] = None) -> pd.Series:
    """Clip series to (lower, upper) bounds, or return unchanged if bounds is None."""
    if bounds is None:
        return s
    lo, hi = bounds
    return s.clip(lo, hi)


def column_for_plot(
    df: pd.DataFrame,
    col: str,
    *,
    bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    clip: bool = True,
) -> pd.Series:
    """Extract column as numeric series, drop NaNs, apply optional clipping from bounds dict."""
    if col not in df.columns:
        raise ValueError(f"Column not found: {col}")

    s = pd.to_numeric(df[col], errors="coerce").dropna()

    if not clip or not bounds:
        return s

    return clip_series(s, bounds.get(col))


# ============================================================================
# Matplotlib Formatting Utilities
# ============================================================================

def apply_plot_style(ax, *, grid_axis: str = "y") -> None:
    """Apply clean matplotlib styling: remove top/right spines, optional y-axis grid, no x-grid."""
    # Remove spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Explicitly disable x-grid (IMPORTANT)
    ax.xaxis.grid(False)

    if grid_axis == "y":
        ax.yaxis.grid(True, linewidth=0.6, alpha=0.25)
    elif grid_axis is None:
        ax.grid(False)
    else:
        raise ValueError("grid_axis must be 'y' or None")



def _format_compact(x: float) -> str:
    """Format numbers compactly: 9500 -> '9.5k', 1250000 -> '1.25M'."""
    ax = abs(x)
    if ax >= 1_000_000:
        return f"{x/1_000_000:.2g}M"
    if ax >= 1_000:
        return f"{x/1_000:.2g}k"
    if ax >= 100:
        return f"{x:.0f}"
    return f"{x:.2g}"


def set_compact_axis(ax, *, axis: str = "x", col: Optional[str] = None) -> None:
    """Apply compact tick formatting to x or y axis. Skips YEAR_COLUMNS to preserve year formatting."""
    from matplotlib.ticker import FuncFormatter
    
    # Skip formatting for year columns - use matplotlib defaults which are better for years
    if col and col in YEAR_COLUMNS:
        return
    
    # Otherwise use compact formatting
    fmt = FuncFormatter(lambda v, pos: _format_compact(v))
    if axis == "x":
        ax.xaxis.set_major_formatter(fmt)
    elif axis == "y":
        ax.yaxis.set_major_formatter(fmt)
    else:
        raise ValueError("axis must be 'x' or 'y'")


# ============================================================================
# High-Level View Builder
# ============================================================================

def build_view(
    df: pd.DataFrame,
    *,
    filter_spec: Optional[Dict[str, Any]] = None,
    clip_cols: Optional[Sequence[str]] = None,
    clip: bool = True,
    p_low: float = 0.01,
    p_high: float = 0.99,
) -> Tuple[pd.DataFrame, Dict[str, Tuple[float, float]]]:
    """Apply filters and compute P1-P99 clip bounds in one step. Returns (filtered_df, bounds_dict)."""
    df_view = apply_filters(df, filter_spec or {})
    bounds = get_clip_bounds(
        df_view,
        cols=clip_cols or [],
        clip=clip,
        p_low=p_low,
        p_high=p_high,
    )
    return df_view, bounds


# ============================================================================
# Plotly Charts and Theming
# ============================================================================

import plotly.express as px
import plotly.graph_objects as go


# Plotly formatting utilities
def _fmt_pln(v: float) -> str:
    """Format PLN values compactly: 16923 -> '16.9k', 1250000 -> '1.25M'."""
    av = abs(v)
    if av >= 1_000_000:
        return f"{v/1_000_000:.2g}M"
    if av >= 1_000:
        return f"{v/1_000:.2g}k"
    return f"{v:.0f}"

def _axis_title(col: str) -> str:
    """Get human-readable axis title for column name."""
    mapping = {
        "price_per_m2": "Price per m² (PLN)",
        "price": "Price (PLN)",
        "area_m2": "Area (m²)",
        "centre_distance": "Distance to centre",
        "poi_count": "POI count",
        "build_year": "Build year",
        "rooms": "Rooms",
        "floor": "Floor",
        "floors_total": "Floors total",
        "school_distance": "School distance",
        "clinic_distance": "Clinic distance",
        "post_office_distance": "Post office distance",
        "kindergarten_distance": "Kindergarten distance",
        "restaurant_distance": "Restaurant distance",
        "college_distance": "College distance",
        "pharmacy_distance": "Pharmacy distance",
        "district": "District",
        "listing_type": "Listing type",
        "condition": "Condition",
        "ownership": "Ownership",
        "building_material": "Building material",
    }
    return mapping.get(col, col.replace("_", " ").title())

def _apply_plotly_theme(fig, *, title: str | None = None) -> None:
    """Apply dark theme styling to Plotly figure: transparent background, subtle grids, clean axes."""
    fig.update_layout(
        title=dict(text=title or "", x=0.0, xanchor="left", font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=55, b=10),
        font=dict(color="rgba(255,255,255,0.86)", size=12),
        showlegend=False,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="rgba(12,16,28,0.96)", font_size=12),
    )

    # subtle axes, no clutter
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color="rgba(255,255,255,0.65)"),
        title_font=dict(color="rgba(255,255,255,0.70)"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color="rgba(255,255,255,0.65)"),
        title_font=dict(color="rgba(255,255,255,0.70)"),
    )




def _plotly_layout(fig, *, title: str | None = None) -> None:
    """Convenience wrapper for _apply_plotly_theme."""
    _apply_plotly_theme(fig, title=title)




def plot_hist(
    df: pd.DataFrame,
    col: str,
    *,
    bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    clip: bool = True,
    bins: int = 30,
    density: bool = False,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    show_median: bool = True,
    median_mode: str = "line",      # kept for backward compat
    return_fig: bool = True,        # kept for backward compat
):
    """Create Plotly histogram with optional clipping, compact formatting, median line, and dark theme."""
    s = column_for_plot(df, col, bounds=bounds, clip=clip)

    fig = px.histogram(
        x=s,
        nbins=bins,
        opacity=1.0,
    )

    # gaps between bars (instead of outlines)
    fig.update_traces(
        marker=dict(color="rgba(32,201,214,0.85)"),
        marker_line_width=0,
    )
    fig.update_layout(bargap=0.25)   # <-- to robi odstępy


    fig.update_layout(
        xaxis_title=xlabel or _axis_title(col),
        yaxis_title="Listings",
    )

    # compact ticks for PLN-like columns
    if col in {"price", "price_per_m2"}:
        fig.update_xaxes(
            tickformat="~s",
            dtick=1000,              # <-- tick co 1k
        )


    if show_median:
        med = float(s.median())
        fig.add_vline(
            x=med,
            line_width=2,
            line_color="rgba(255,180,0,0.9)",
        )
        fig.add_annotation(
            x=med,
            y=1.02,
            yref="paper",
            text=f"median · {_fmt_pln(med)}",
            showarrow=False,
            font=dict(size=12, color="rgba(255,180,0,0.95)"),
        )

    _plotly_layout(fig, title=title or f"{_axis_title(col)} distribution")
    return fig



def plot_box(
    df: pd.DataFrame,
    col: str,
    *,
    bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    clip: bool = True,
    title: Optional[str] = None,
    ylabel: Optional[str] = None,
    show_fliers: bool = False,  # plotly shows points via 'points'
    return_fig: bool = True,
):
    """Create Plotly boxplot with optional clipping and outlier display."""
    s = column_for_plot(df, col, bounds=bounds, clip=clip)
    fig = go.Figure()
    fig.add_trace(go.Box(y=s, boxpoints=False if not show_fliers else "outliers"))
    fig.update_layout(yaxis_title=ylabel or col)
    _plotly_layout(fig, title=title or f"Boxplot: {col}")
    return fig


def plot_box_by_category(
    df: pd.DataFrame,
    *,
    y: Optional[str] = None,
    cat: Optional[str] = None,
    y_col: Optional[str] = None,
    category_col: Optional[str] = None,
    bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    clip: bool = True,
    min_n: int = 50,
    sort_by: str = "median",
    order: Optional[list] = None,
    title: Optional[str] = None,
    ylabel: Optional[str] = None,
    rotate_x: int = 45,
    return_fig: bool = True,
):
    """Create grouped boxplot by category with min_n filtering, optional sorting (median/count), and display label mapping."""
    y = y or y_col
    cat = cat or category_col
    if not y or not cat:
        raise ValueError("plot_box_by_category requires 'y' and 'cat' (or aliases).")

    x = df[[cat, y]].copy()
    x[y] = pd.to_numeric(x[y], errors="coerce")
    x = x.dropna(subset=[cat, y])

    if clip and bounds and y in bounds:
        lo, hi = bounds[y]
        x[y] = x[y].clip(lo, hi)

    stats = x.groupby(cat)[y].agg(n="size", median="median").reset_index()
    stats = stats[stats["n"] >= min_n]
    if stats.empty:
        raise ValueError(f"No categories meet min_n={min_n} for '{cat}'.")

    if order is None:
        # For binned columns, preserve natural order (don't sort by median)
        if cat.endswith('_bin'):
            # Get unique categories in their original order (pandas Categorical preserves order)
            order = [c for c in x[cat].cat.categories if c in stats[cat].values] if hasattr(x[cat], 'cat') else stats[cat].tolist()
        elif sort_by == "median":
            order = stats.sort_values("median")[cat].tolist()
        elif sort_by == "count":
            order = stats.sort_values("n")[cat].tolist()
        else:
            raise ValueError("sort_by must be 'median' or 'count'")

    x[cat] = pd.Categorical(x[cat], categories=order, ordered=True)
    x = x.sort_values(cat)

    # Map raw values to display labels
    x_display = x.copy()
    x_display[cat] = x_display[cat].apply(lambda v: label_for_value(cat, str(v)))

    fig = px.box(x_display, x=cat, y=y, points=False)
    fig.update_layout(
        xaxis_tickangle=rotate_x,
        xaxis_title=column_label(cat),
        yaxis_title=column_label(y),
    )

    # subtle box styling
    fig.update_traces(
        fillcolor="rgba(32,201,214,0.6)",
        line=dict(color="rgba(32,201,214,1.0)", width=1.5),
        marker=dict(color="rgba(32,201,214,0.5)", size=4),
        opacity=0.9,
    )




    if y in {"price", "price_per_m2"}:
        fig.update_yaxes(tickformat="~s")

    _plotly_layout(fig, title=title or f"{_axis_title(y)} by {_axis_title(cat)}")
    return fig


def plot_scatter(
    df: pd.DataFrame,
    *,
    x: Optional[str] = None,
    y: Optional[str] = None,
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
    bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    clip: bool = True,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    alpha: float = 0.25,
    trendline: bool = False,
    return_fig: bool = True,
):
    """Create Plotly scatter plot with optional clipping, OLS trendline, and compact axis formatting."""
    xcol = x or x_col
    ycol = y or y_col
    if not xcol or not ycol:
        raise ValueError("plot_scatter requires x and y.")

    d = df[[xcol, ycol]].copy()
    d[xcol] = pd.to_numeric(d[xcol], errors="coerce")
    d[ycol] = pd.to_numeric(d[ycol], errors="coerce")
    d = d.dropna(subset=[xcol, ycol])

    if clip and bounds:
        if xcol in bounds:
            lo, hi = bounds[xcol]
            d[xcol] = d[xcol].clip(lo, hi)
        if ycol in bounds:
            lo, hi = bounds[ycol]
            d[ycol] = d[ycol].clip(lo, hi)

    fig = px.scatter(
        d,
        x=xcol,
        y=ycol,
        opacity=alpha,
        trendline="ols" if trendline else None,
    )

    # point styling
    fig.update_traces(marker=dict(size=6, color="rgba(16,196,212,0.55)"))

    fig.update_layout(
        xaxis_title=xlabel or _axis_title(xcol),
        yaxis_title=ylabel or _axis_title(ycol),
    )

    if xcol in {"price", "price_per_m2"}:
        fig.update_xaxes(tickformat="~s")
    if ycol in {"price", "price_per_m2"}:
        fig.update_yaxes(tickformat="~s")

    _plotly_layout(fig, title=title or f"{_axis_title(ycol)} vs {_axis_title(xcol)}")
    return fig




def apply_dashboard_theme(fig, title: str):
    """Apply consistent dark theme to Plotly figure: transparent background, subtle grids, teal markers."""
    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=55, b=10),
        font=dict(color="rgba(255,255,255,0.90)", size=13),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False),
    )
    fig.update_traces(marker_color="#10C4D4")
    return fig


