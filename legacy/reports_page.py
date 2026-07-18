from __future__ import annotations

import streamlit as st

from backend.model_manager import get_model_manager
from reports.pdf_report import build_prediction_pdf


def render_reports() -> None:
    st.title("Reports")
    manager = get_model_manager()
    models = manager.list_models()
    if models:
        selected_id = st.selectbox(
            "Model",
            [record.model_id for record in models],
            format_func=lambda model_id: next(record.drug_name for record in models if record.model_id == model_id),
            help="Export model-level PDF, CSV, or JSON reports.",
        )
        record = next(record for record in models if record.model_id == selected_id)
        c1, c2, c3 = st.columns(3)
        c1.download_button("Export PDF", manager.export_pdf(record), f"{record.model_id}_model_report.pdf", "application/pdf", use_container_width=True)
        c2.download_button("Export CSV", manager.export_csv(record), f"{record.model_id}_model_report.csv", "text/csv", use_container_width=True)
        c3.download_button("Export JSON", manager.export_json(record), f"{record.model_id}_training_report.json", "application/json", use_container_width=True)
        st.json({"summary": record.summary, "diagnostics": record.diagnostics})
        st.divider()

    predictions = st.session_state.get("last_predictions")
    if predictions is None or predictions.empty:
        st.info("Run a single or batch prediction to generate a downloadable report.")
        return
    active = manager.get_active_model()

    rows = st.slider("Rows to include", 1, min(len(predictions), 50), min(len(predictions), 10))
    pdf = build_prediction_pdf(
        predictions.head(rows),
        model_summary=active.summary if active else None,
        diagnostics=active.diagnostics if active else None,
    )
    st.dataframe(predictions.head(rows), hide_index=True, use_container_width=True)
    st.download_button(
        "Generate PDF",
        data=pdf,
        file_name="qube_predict_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
