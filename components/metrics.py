"""Metric cards and summary components."""

from __future__ import annotations

from typing import Any

import streamlit as st


def metric_card(label: str, value: str, delta: str | None = None) -> None:
    """Render a compact KPI card."""

    delta_html = f'<div class="qrei-card-delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="qrei-card">
          <div class="qrei-card-label">{label}</div>
          <div class="qrei-card-value">{value}</div>
          {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_grid(items: list[tuple[str, Any, str | None]], columns: int = 4) -> None:
    """Render KPI cards in a responsive Streamlit grid."""

    cols = st.columns(columns)
    for idx, (label, value, delta) in enumerate(items):
        with cols[idx % columns]:
            metric_card(label, str(value), delta)


def warning_from_payload(payload: dict[str, Any]) -> None:
    """Show backend fallback warning when present."""

    if payload.get("_api_warning"):
        st.info(payload["_api_warning"])