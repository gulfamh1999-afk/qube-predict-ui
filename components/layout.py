"""Layout and navigation components."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from services.api_client import QREIClient
from utils.session import init_state

ROOT = Path(__file__).resolve().parents[1]


def setup_page(title: str, subtitle: str | None = None) -> QREIClient:
    """Apply global page setup and return an API client."""

    init_state()
    st.set_page_config(
        page_title=f"{title} | QREI",
        page_icon=str(ROOT / "assets" / "icon.svg"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css()
    render_sidebar()
    st.markdown('<div class="qrei-shell">', unsafe_allow_html=True)
    st.markdown(f'<h1 class="qrei-title">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="qrei-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    return QREIClient(st.session_state.api_base_url, st.session_state.use_api)


def finish_page() -> None:
    """Close shared page wrapper."""

    st.markdown("</div>", unsafe_allow_html=True)


def load_css() -> None:
    """Load dashboard CSS."""

    css_path = ROOT / "styles" / "dashboard.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_sidebar() -> None:
    """Render common sidebar settings and navigation hints."""

    with st.sidebar:
        st.image(str(ROOT / "assets" / "icon.svg"), width=58)
        st.title("QREI Dashboard")
        st.caption("Real estate intelligence workspace")
        st.divider()
        st.session_state.use_api = st.toggle("Use FastAPI backend", value=st.session_state.use_api)
        st.session_state.api_base_url = st.text_input("API base URL", st.session_state.api_base_url)
        st.session_state.theme_mode = st.radio("Theme", ["Dark", "Light"], horizontal=True, index=0)
        st.divider()
        st.caption("Open pages from the app navigation.")
        st.caption("Autosave, history, and bookmarks are stored in this session.")