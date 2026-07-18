from __future__ import annotations

from datetime import datetime

import streamlit as st

from backend.model_manager import ManagedModel, get_model_manager
from backend.navigation import navigate_to


def render_models() -> None:
    st.title("Models")
    st.caption("Train, load, compare, export, and delete QUBE Predict models.")
    manager = get_model_manager()
    models = manager.list_models()
    active = manager.get_active_model()

    if not models:
        st.info("No models registered yet. Train a model in Settings or save one to models/<drug_name>/.")
        if st.button("Open Settings", use_container_width=True):
            navigate_to("Settings")
            st.rerun()
        return

    st.metric("Active Model", active.drug_name if active else "None")

    for record in models:
        _model_card(manager, record, is_active=bool(active and active.model_id == record.model_id))


def _model_card(manager, record: ManagedModel, *, is_active: bool) -> None:
    metrics = record.summary.get("metrics", {})
    trained = record.summary.get("training_date", "NA")
    try:
        trained = datetime.fromisoformat(trained).strftime("%d-%b-%Y")
    except Exception:
        pass

    with st.container(border=True):
        top = st.columns([2.2, 1, 1, 1, 1])
        top[0].subheader(("Active: " if is_active else "") + record.drug_name)
        top[1].metric("Samples", record.summary.get("samples", "NA"))
        top[2].metric("Descriptors", record.summary.get("selected_descriptors", "NA"))
        top[3].metric("RF trees", record.summary.get("rf_trees", "NA"))
        top[4].metric("CV Accuracy", _fmt(metrics.get("accuracy")))

        st.caption(f"Trained: {trained} | Save location: {record.model_path or 'Session only'}")

        c1, c2, c3, c4 = st.columns(4)
        if c1.button("Load", key=f"load_{record.model_id}", use_container_width=True):
            manager.load_model(record.model_id)
            st.success(f"{record.drug_name} is now active.")
            st.rerun()
        if c2.button("Predict", key=f"predict_{record.model_id}", use_container_width=True):
            manager.load_model(record.model_id)
            navigate_to("Single Prediction")
            st.rerun()
        c3.download_button(
            "Export",
            data=manager.export_json(record),
            file_name=f"{record.model_id}_training_report.json",
            mime="application/json",
            key=f"export_{record.model_id}",
            use_container_width=True,
        )
        if c4.button("Delete", key=f"delete_{record.model_id}", use_container_width=True):
            manager.delete_model(record.model_id)
            st.warning(f"Deleted {record.drug_name}.")
            st.rerun()


def _fmt(value) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)
