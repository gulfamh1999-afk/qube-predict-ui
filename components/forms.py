"""Input form helpers."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.importers import parse_uploaded_points
from utils.session import add_history, set_points


def coordinate_editor(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Render editable coordinate table."""

    frame = pd.DataFrame(points, columns=["x", "y"])
    edited = st.data_editor(frame, num_rows="dynamic", use_container_width=True, key="coordinate_editor")
    clean = edited.dropna().astype(float)
    return [(float(row["x"]), float(row["y"])) for _, row in clean.iterrows()]


def import_panel() -> None:
    """Render upload/import panel."""

    uploaded = st.file_uploader("Import parcel", type=["csv", "xlsx", "xls", "geojson", "json", "zip", "kml"])
    if uploaded:
        try:
            points = parse_uploaded_points(uploaded)
            set_points(points)
            st.success(f"Imported {len(points)} coordinates from {uploaded.name}.")
        except Exception as exc:
            st.error(f"Import failed: {exc}")


def parcel_actions() -> None:
    """Render common parcel editing actions."""

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Undo", use_container_width=True) and st.session_state.parcel_points:
            st.session_state.redo_points.append(st.session_state.parcel_points.pop())
            add_history("Undo point")
            st.rerun()
    with col2:
        if st.button("Redo", use_container_width=True) and st.session_state.redo_points:
            st.session_state.parcel_points.append(st.session_state.redo_points.pop())
            add_history("Redo point")
            st.rerun()
    with col3:
        if st.button("Delete last", use_container_width=True) and st.session_state.parcel_points:
            st.session_state.parcel_points.pop()
            add_history("Deleted last point")
            st.rerun()
    with col4:
        if st.button("Reset", use_container_width=True):
            from utils.session import DEFAULT_POINTS

            st.session_state.parcel_points = list(DEFAULT_POINTS)
            st.session_state.redo_points = []
            add_history("Reset parcel")
            st.rerun()