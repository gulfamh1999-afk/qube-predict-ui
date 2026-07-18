from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.model_manager import get_model_manager


def render_model_diagnostics() -> None:
    st.title("Model Diagnostics")
    manager = get_model_manager()
    active = manager.get_active_model()
    if not active:
        st.info("Train or load a model to inspect QUBE2 diagnostics.")
        return
    st.caption(f"Active Model: {active.drug_name}")
    report = active.diagnostics

    graph = report.get("graph", {})
    cols = st.columns(5)
    for col, key in zip(cols, ["nodes", "edges", "connected_components", "removed_constant_features", "density"]):
        col.metric(key.replace("_", " ").title(), graph.get(key, "NA"))

    st.subheader("Descriptor Bank")
    st.json(
        {
            "Expanded descriptors": report.get("expanded_features"),
            "Selected descriptors": report.get("descriptor_bank_features"),
            "Configuration": report.get("config"),
            "Model metadata": active.summary,
        }
    )

    quality = report.get("descriptor_quality", {})
    top = pd.DataFrame(quality.get("top_selected_descriptors", []))
    if not top.empty:
        st.dataframe(top, use_container_width=True, hide_index=True)
    st.subheader("Feature Selection Report")
    st.json({k: v for k, v in quality.items() if k != "top_selected_descriptors"})
