from __future__ import annotations

import streamlit as st

from backend.model_manager import get_model_manager
from backend.metrics import drug_library_frame


def render_drug_library() -> None:
    st.title("Drug Library")
    st.subheader("Built-in Library")
    df = drug_library_frame()
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Accuracy": st.column_config.ProgressColumn("Accuracy", min_value=0, max_value=1),
            "ROC-AUC": st.column_config.ProgressColumn("ROC-AUC", min_value=0, max_value=1),
        },
    )
    st.subheader("User Models")
    manager = get_model_manager()
    models = manager.list_models()
    if not models:
        st.info("No user-trained models yet.")
        return
    rows = []
    for record in models:
        metrics = record.summary.get("metrics", {})
        rows.append(
            {
                "Model": record.drug_name,
                "Samples": record.summary.get("samples"),
                "Genes": record.summary.get("genes") or record.summary.get("features"),
                "Accuracy": metrics.get("accuracy"),
                "F1": metrics.get("f1"),
                "Saved": bool(record.persisted),
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)
