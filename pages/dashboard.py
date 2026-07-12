from __future__ import annotations

import streamlit as st

from backend.config import ENGINE_METADATA
from backend.metrics import drug_library_frame
from backend.model_manager import get_model_manager
from ui.charts import accuracy_chart, distribution_chart, roc_chart
from ui.theme import hero, metric_card, status_pill


def render_dashboard() -> None:
    manager = get_model_manager()
    models = manager.list_models()
    active = manager.get_active_model()
    hero()
    status_pill(ENGINE_METADATA.validation_status)

    st.markdown("#### Home")
    cols = st.columns(4)
    latest = _latest_training_date(models)
    averages = _average_metrics(models)
    builtin = drug_library_frame()
    home = {
        "Engine": ENGINE_METADATA.engine_version,
        "Models trained": len(models),
        "Active model": active.drug_name if active else "None",
        "Latest trained": latest,
        "Mean Cross Validation Accuracy": _fmt(averages.get("accuracy")),
        "Average F1": _fmt(averages.get("f1")),
        "Mean ROC-AUC": _fmt(averages.get("roc_auc")),
        "Number of folds": active.summary.get("metrics", {}).get("folds", "NA") if active else "NA",
        "Validation dataset size": active.summary.get("metrics", {}).get("validation_dataset_size", "NA") if active else "NA",
        "Built-in validated drugs": len(builtin),
        "Total descriptors": active.summary.get("selected_descriptors", "NA") if active else "NA",
        "Graph nodes": active.diagnostics.get("graph", {}).get("nodes", "NA") if active else "NA",
    }
    for col, (label, value) in zip(st.columns(4) * 3, home.items()):
        with col:
            metric_card(label, value)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(accuracy_chart(), use_container_width=True)
    with right:
        st.plotly_chart(roc_chart(), use_container_width=True)
    st.plotly_chart(distribution_chart(st.session_state.get("last_predictions")), use_container_width=True)


def _average_metrics(models) -> dict:
    values = {}
    for metric in ("accuracy", "f1", "roc_auc"):
        nums = [
            record.summary.get("metrics", {}).get(metric)
            for record in models
            if record.summary.get("metric_source") == "cross_validation"
            and record.summary.get("metrics", {}).get(metric) is not None
        ]
        values[metric] = sum(nums) / len(nums) if nums else None
    return values


def _latest_training_date(models) -> str:
    dates = [record.summary.get("training_date") for record in models if record.summary.get("training_date")]
    if not dates:
        return "NA"
    latest = max(dates)
    return "Today" if latest[:10] == ENGINE_METADATA.build_date else latest[:10]


def _fmt(value) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)
