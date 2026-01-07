"""UI components and styling for Streamlit dashboard with dark theme and custom cards."""

from __future__ import annotations
import streamlit as st
from contextlib import contextmanager
from functools import lru_cache


# ============================================================================
# Inline SVG Icons
# ============================================================================

_ICONS = {
    "home": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M5 12l7-7l7 7"/>
  <path d="M9 21V9h6v12"/>
</svg>
""",
    "building": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 21h18"/>
  <path d="M6 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16"/>
  <path d="M9 8h1M9 12h1M9 16h1"/>
  <path d="M14 8h1M14 12h1M14 16h1"/>
</svg>
""",
    "chart": """
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 3v18h18"/>
  <path d="M7 15l4-4l4 4l5-6"/>
</svg>
""",
}

@lru_cache(maxsize=64)
def icon(name: str, size: int = 18) -> str:
    """Get cached SVG icon HTML with specified size."""
    svg = _ICONS.get(name)
    if not svg:
        return ""
    return (
        f'<span class="ui-icon" style="width:{size}px;height:{size}px">'
        f'{svg}</span>'
    )


# ============================================================================
# Global CSS Injection
# ============================================================================

def inject_global_css() -> None:
    """Inject dark theme CSS with gradient backgrounds, card styling, and sidebar design."""
    st.markdown(
        """
<style>
/* --- App background with radial gradients --- */
.stApp {
  background: radial-gradient(1200px 600px at 20% 0%, rgba(16,196,212,0.10), transparent 55%),
              radial-gradient(900px 500px at 95% 10%, rgba(99,102,241,0.10), transparent 60%),
              #070B14;
  color: rgba(255,255,255,0.92);
}

/* --- Typography --- */
html, body, [class*="css"]  {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* --- Remove Streamlit paddings a bit, more airy --- */
.main .block-container {
  padding-top: 1.1rem;
  padding-bottom: 2.2rem;
  max-width: 1240px;
}

/* =========================
   Sidebar Styling
   ========================= */

/* Sidebar container with dark background */
section[data-testid="stSidebar"] {
  background: rgba(12, 14, 18, 0.98) !important;
  border-right: 1px solid rgba(255,255,255,0.06) !important;
}

/* Sidebar padding + width feel */
section[data-testid="stSidebar"] > div {
  padding-top: 14px !important;
}

/* Sidebar title/header area */
.sidebar-title {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.2px;
  color: rgba(255,255,255,0.92);
  margin: 2px 0 10px 0;
}

/* Section container (card-like) */
.sidebar-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 12px 12px 6px 12px;
  margin-bottom: 10px;
  box-shadow: 0 8px 18px rgba(0,0,0,0.25);
}

/* Section label */
.sidebar-section-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  font-weight: 650;
  color: rgba(255,255,255,0.78);
  margin-bottom: 8px;
}

/* Accent dot (teal) */
.sidebar-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(32,201,214,0.95);
  box-shadow: 0 0 0 4px rgba(32,201,214,0.12);
}

/* Make widgets look consistent */
section[data-testid="stSidebar"] .stMultiSelect,
section[data-testid="stSidebar"] .stSelectbox,
section[data-testid="stSidebar"] .stNumberInput,
section[data-testid="stSidebar"] .stSlider,
section[data-testid="stSidebar"] .stTextInput {
  margin-bottom: 10px !important;
}

/* Streamlit labels */
section[data-testid="stSidebar"] label {
  color: rgba(255,255,255,0.72) !important;
  font-weight: 600 !important;
  font-size: 12px !important;
}

/* Input boxes */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] .stMultiSelect div[role="combobox"],
section[data-testid="stSidebar"] .stSelectbox div[role="combobox"] {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 12px !important;
  color: rgba(255,255,255,0.92) !important;
}

/* Slider track */
section[data-testid="stSidebar"] [data-baseweb="slider"] div[role="slider"] {
  box-shadow: 0 0 0 4px rgba(32,201,214,0.12) !important;
}

/* Checkbox row */
section[data-testid="stSidebar"] .stCheckbox {
  padding: 4px 0 !important;
}

/* Divider replacement: subtle spacing (no grey hr lines) */
section[data-testid="stSidebar"] hr,
section[data-testid="stSidebar"] [data-testid="stDivider"] {
  display: none !important;
}


/* --- Headings spacing --- */
h1, h2, h3 {
  letter-spacing: -0.02em;
}
h1 { font-size: 30px; }
h2 { font-size: 20px; margin-top: 0.2rem; }
h3 { font-size: 16px; opacity: 0.92; }

/* --- “Card” container --- */
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 16px 16px 10px 16px;
  box-shadow: 0 10px 35px rgba(0,0,0,0.35);
}

/* --- KPI cards --- */
.kpi-title {
  font-size: 12px;
  opacity: 0.72;
  margin-bottom: 2px;
}
.kpi-value {
  font-size: 28px;
  font-weight: 750;
  letter-spacing: -0.02em;
}
.kpi-sub {
  font-size: 12px;
  opacity: 0.65;
  margin-top: 2px;
}

/* --- Inputs --- */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 12px !important;
}

div[data-baseweb="slider"] {
  padding-top: 6px;
}

/* --- Plotly chart container --- */
div[data-testid="stPlotlyChart"] {
  background: transparent;
}

/* --- Divider --- */
hr {
  border-color: rgba(255,255,255,0.08) !important;
}



/* --- Hide “made with streamlit” footer --- */
footer { visibility: hidden; }
/* --- Hide Streamlit skeleton loaders (grey bars) --- */
[data-testid="stSkeleton"] {
  display: none !important;
}





/* =========================
   Card Containers (Lovable-style)
   ========================= */

:root{
  --bg: #0b0f16;
  --card1: rgba(18, 24, 36, 0.72);
  --card2: rgba(10, 14, 22, 0.72);
  --stroke: rgba(255,255,255,0.07);
  --stroke2: rgba(255,255,255,0.04);
  --shadow: rgba(0,0,0,0.55);
}

/* Fallback: Style ALL columns with Plotly charts (works in all browsers) */
[data-testid="column"] {
  position: relative;
  border-radius: 18px;
  padding: 18px 18px 14px 18px;

  /* gradient INSIDE the card */
  background:
    radial-gradient(1200px 420px at 10% 0%,
      rgba(32,201,214,0.14) 0%,
      rgba(32,201,214,0.06) 28%,
      rgba(255,255,255,0.00) 60%),
    linear-gradient(180deg, var(--card1) 0%, var(--card2) 100%);

  border: 1px solid var(--stroke);
  box-shadow:
    0 18px 45px var(--shadow),
    inset 0 1px 0 rgba(255,255,255,0.06);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
}

/* Modern browsers: only style columns containing Plotly charts (overrides above if supported) */
@supports selector(:has(*)) {
  [data-testid="column"] {
    /* Reset styles for empty columns */
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
  }
  
  [data-testid="column"]:has([data-testid="stPlotlyChart"]) {
    position: relative;
    border-radius: 18px;
    padding: 18px 18px 14px 18px;
    background:
      radial-gradient(1200px 420px at 10% 0%,
        rgba(32,201,214,0.14) 0%,
        rgba(32,201,214,0.06) 28%,
        rgba(255,255,255,0.00) 60%),
      linear-gradient(180deg, var(--card1) 0%, var(--card2) 100%);
    border: 1px solid var(--stroke);
    box-shadow:
      0 18px 45px var(--shadow),
      inset 0 1px 0 rgba(255,255,255,0.06);
    -webkit-backdrop-filter: blur(10px);
    backdrop-filter: blur(10px);
  }
}

/* subtle inner highlight ring */
[data-testid="column"]::after{
  content:"";
  position:absolute;
  inset:0;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  border-radius:18px;
  pointer-events:none;
  border: 1px solid var(--stroke2);
}

/* make plotly full-bleed inside cards */
[data-testid="column"] .js-plotly-plot,
[data-testid="column"] [data-testid="stPlotlyChart"]{
  margin-top: 6px;
}

/* remove extra vertical gaps Streamlit adds around blocks inside cards */
[data-testid="column"] [data-testid="stVerticalBlock"]{
  gap: 0.65rem;
}

/* Legacy .card class support for kpi_card() function */
.card {
  position: relative;
  border-radius: 18px;
  padding: 18px 18px 14px 18px;
  background:
    radial-gradient(1200px 420px at 10% 0%,
      rgba(32,201,214,0.14) 0%,
      rgba(32,201,214,0.06) 28%,
      rgba(255,255,255,0.00) 60%),
    linear-gradient(180deg, var(--card1) 0%, var(--card2) 100%);
  border: 1px solid var(--stroke);
  box-shadow:
    0 18px 45px var(--shadow),
    inset 0 1px 0 rgba(255,255,255,0.06);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
}

.card::after{
  content:"";
  position:absolute;
  inset:0;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  border-radius:18px;
  pointer-events:none;
  border: 1px solid var(--stroke2);
}

/* --- Icons --- */
.ui-icon svg {
  width: 100%;
  height: 100%;
  color: rgba(32,201,214,0.95);
}

/* --- Fix icon sizing --- */
.ui-icon {
  display: inline-flex;
  width: 16px;
  height: 16px;
  flex: 0 0 16px;
}

.ui-icon svg {
  width: 100%;
  height: 100%;
  display: block;
}




</style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# UI Components
# ============================================================================

def header(title: str, subtitle: str) -> None:
    """Render page header with icon, title, and subtitle."""
    st.markdown(
        f"""
<div style="display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:8px;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:44px;height:44px;border-radius:14px;
                background:rgba(16,196,212,0.16);
                border:1px solid rgba(16,196,212,0.25);
                display:flex;align-items:center;justify-content:center;font-size:20px;">
      🏠
    </div>
    <div>
      <div style="font-size:22px;font-weight:800;line-height:1.1;">{title}</div>
      <div style="font-size:12px;opacity:0.65;margin-top:2px;">{subtitle}</div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def card():
    """Context manager for styled card container. Usage: with card(): st.plotly_chart(fig)"""
    # Create a container and target it with CSS via data-testid
    container = st.container()
    with container:
        yield


def kpi_card(title: str, value: str, sub: str = "", trend: float | None = None) -> None:
    """
    Display KPI card with optional month-over-month trend indicator.
    
    Args:
        title: Card title
        value: Main value to display
        sub: Subtitle/description
        trend: Optional percentage change (e.g., 5.2 for +5.2%, -1.5 for -1.5%)
    """
    trend_html = ""
    if trend is not None:
        if trend > 0:
            arrow = "↑"
            color = "#10b981"  # green
            sign = "+"
        elif trend < 0:
            arrow = "↓"
            color = "#ef4444"  # red
            sign = ""
        else:
            arrow = ""
            color = "#6b7280"  # gray
            sign = ""
        
        trend_html = f'<div class="kpi-trend" style="color: {color}; font-size: 0.875rem; margin-top: 0.5rem;">{arrow} {sign}{abs(trend):.1f}% vs last month</div>'
    
    st.markdown(
        f"""
<div class="card">
  <div class="kpi-title">{title}</div>
  <div class="kpi-value">{value}</div>
  <div class="kpi-sub">{sub}</div>
  {trend_html}
</div>
        """,
        unsafe_allow_html=True,
    )




