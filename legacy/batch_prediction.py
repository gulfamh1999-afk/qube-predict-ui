from __future__ import annotations

import streamlit as st

from backend.data import read_uploaded_table
from backend.model_manager import get_model_manager
from backend.qube_wrapper import predict_dataframe
from ui.charts import distribution_chart


def render_batch_prediction() -> None:
    st.title("Batch Prediction")
    st.caption("Predict every sample in an uploaded expression matrix.")

    manager = get_model_manager()
    models = manager.list_models()
    if not models:
        st.warning("Load or train a model in Settings before running batch prediction.")
        return
    active = manager.get_active_model()
    selected_id = st.selectbox(
        "Active model",
        [record.model_id for record in models],
        index=[record.model_id for record in models].index(active.model_id) if active else 0,
        format_func=lambda model_id: next(record.drug_name for record in models if record.model_id == model_id),
        help="Only trained or saved models appear here. Batch prediction uses this selected model.",
    )
    active = manager.load_model(selected_id)

    uploaded = st.file_uploader(
        "Multi-sample CSV/XLSX",
        type=["csv", "xlsx", "xls"],
        key="batch_upload",
        help="Upload multiple samples for scoring. Each row is one sample; numeric columns are aligned to the active model's training features.",
    )
    if uploaded is None:
        return

    df = read_uploaded_table(uploaded)
    st.caption(f"{len(df):,} rows uploaded")
    if st.button(
        "Run batch prediction",
        use_container_width=True,
        help="Scores every uploaded row with the active QUBE2 model.",
    ):
        with st.spinner("Transforming graph descriptors and predicting response..."):
            st.session_state.last_predictions = predict_dataframe(active.model, active.feature_names, df, active.drug_name)

    predictions = st.session_state.get("last_predictions")
    if predictions is None:
        return

    query = st.text_input(
        "Search results",
        help="Filter the prediction table by sample id, drug, response label, probability, or risk score.",
    )
    filtered = predictions
    if query:
        mask = filtered.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        filtered = filtered[mask]

    classes = st.multiselect(
        "Filter prediction",
        sorted(predictions["prediction"].unique()),
        default=sorted(predictions["prediction"].unique()),
        help="Show only selected response classes in the batch table.",
    )
    filtered = filtered[filtered["prediction"].isin(classes)]
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.plotly_chart(distribution_chart(filtered), use_container_width=True)
    st.download_button(
        "Download CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="qube_batch_predictions.csv",
        mime="text/csv",
        use_container_width=True,
        help="Exports the currently filtered prediction table.",
    )
