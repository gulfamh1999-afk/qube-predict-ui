from __future__ import annotations

from pathlib import Path

import streamlit as st

from backend.config import ENGINE_METADATA, ROOT_DIR
from backend.model_manager import get_model_manager
from backend.navigation import PAGE_KEY, initialize_navigation


def apply_theme() -> None:
    css_path = ROOT_DIR / "assets" / "qube_predict.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_sidebar(pages: list[str]) -> str:
    manager = get_model_manager()
    initialize_navigation(pages[0], pages)
    active = manager.get_active_model()
    with st.sidebar:
        st.image(str(ROOT_DIR / "assets" / "icon.svg"), width=52)
        st.markdown("### QUBE Predict")
        st.caption("Graph-Based Drug Response Prediction")
        st.radio("Navigation", pages, key=PAGE_KEY, label_visibility="collapsed")
        st.divider()
        st.markdown(f"**Engine**  \n{ENGINE_METADATA.engine_version}")
        st.markdown(f"**Active Model**  \n{active.drug_name if active else 'No active model'}")
    return st.session_state[PAGE_KEY]


def hero(title: str = "QUBE Predict", subtitle: str = "Graph-Based Drug Response Prediction Platform") -> None:
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-title">{title}<sup style="font-size:.28em;">TM</sup></div>
          <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: object, help_text: str | None = None) -> None:
    help_html = f'<div class="small-muted">{help_text}</div>' if help_text else ""
    title = f' title="{help_text}"' if help_text else ""
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


def status_pill(text: str) -> None:
    st.markdown(f'<span class="status-pill">{text}</span>', unsafe_allow_html=True)
