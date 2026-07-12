from __future__ import annotations

from pathlib import Path

import streamlit as st

# ==========================================================
# FRONTEND CONFIGURATION
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
PAGE_KEY = "page"

APP_NAME = "QUBE Predict"
APP_SUBTITLE = "Graph-Based Drug Response Prediction Platform"
ENGINE_VERSION = "Cloud API"

# ==========================================================
# THEME
# ==========================================================

def apply_theme() -> None:
    css_path = ROOT_DIR / "assets" / "qube_predict.css"

    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )

# ==========================================================
# SIDEBAR
# ==========================================================

def render_sidebar(pages: list[str]) -> str:

    if PAGE_KEY not in st.session_state:
        st.session_state[PAGE_KEY] = pages[0]

    with st.sidebar:

        icon_path = ROOT_DIR / "assets" / "icon.svg"

        if icon_path.exists():
            st.image(str(icon_path), width=52)

        st.markdown(f"### {APP_NAME}")
        st.caption(APP_SUBTITLE)

        st.radio(
            "Navigation",
            pages,
            key=PAGE_KEY,
            label_visibility="collapsed",
        )

        st.divider()

        st.markdown(f"**Engine**  \n{ENGINE_VERSION}")

        api_url = st.session_state.get(
            "api_url",
            "Not Connected"
        )

        st.markdown(f"**Backend**  \n{api_url}")

    return st.session_state[PAGE_KEY]

# ==========================================================
# HERO
# ==========================================================

def hero(
    title: str = APP_NAME,
    subtitle: str = APP_SUBTITLE,
) -> None:

    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-title">
            {title}<sup style="font-size:.28em;">TM</sup>
          </div>

          <div class="hero-subtitle">
            {subtitle}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================================
# METRIC CARD
# ==========================================================

def metric_card(
    label: str,
    value: object,
    help_text: str | None = None,
) -> None:

    help_html = (
        f'<div class="small-muted">{help_text}</div>'
        if help_text
        else ""
    )

    title = (
        f' title="{help_text}"'
        if help_text
        else ""
    )

    st.markdown(
        f"""
        <div class="metric-card"{title}>
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          {help_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================================
# STATUS PILL
# ==========================================================

def status_pill(text: str) -> None:

    st.markdown(
        f'<span class="status-pill">{text}</span>',
        unsafe_allow_html=True,
    )