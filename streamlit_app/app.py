# streamlit_app/app.py
import sys
from pathlib import Path

# Add src/ to Python path for apartments package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st

st.set_page_config(page_title="Apartments Dashboard", layout="wide")

st.markdown(
    """
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
      <div style="width:44px;height:44px;border-radius:12px;background:rgba(16,196,212,0.15);
                  display:flex;align-items:center;justify-content:center;font-size:20px;">🏠</div>
      <div>
        <div style="font-size:26px;font-weight:700;line-height:1.1;">Apartments Dashboard</div>
        <div style="opacity:0.75;">Real-time Warsaw market analytics</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info("Choose a page from the sidebar (Pages).")

# streamlit run streamlit_app/app.py