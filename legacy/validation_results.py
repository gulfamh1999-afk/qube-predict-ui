from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from backend.metrics import builtin_fold_results, drug_library_frame, load_builtin_validation_results
from backend.model_manager import get_model_manager


def render_validation_results() -> None:
    st.title("Validation Results")
    st.caption("Built-in validation benchmarks and user-trained session models.")
    df = drug_library_frame()
    raw = load_builtin_validation_results()

    st.subheader("Built-in Validation Library")
    if df.empty:
        st.warning("No built-in validation results were found in validation/multi_drug_results.csv or the project root.")
    else:
        st.dataframe(df, hide_index=True, use_container_width=True)

    st.subheader("Accuracy Comparison")
    if not df.empty:
        st.plotly_chart(px.bar(df, x="Drug", y="Accuracy", template="plotly_white"), use_container_width=True)

    st.subheader("ROC Comparison")
    if not df.empty:
        st.plotly_chart(px.line(df, x="Drug", y="ROC-AUC", markers=True, template="plotly_white"), use_container_width=True)

    st.subheader("Benchmark Comparisons")
    if not raw.empty:
        comparison_cols = [
            col for col in [
                "Drug",
                "RF Accuracy",
                "RF ROC-AUC",
                "ExtraTrees Accuracy",
                "XGBoost Accuracy",
                "LightGBM Accuracy",
                "QUBE2 Accuracy",
                "QUBE2 ROC-AUC",
                "Random Feature Accuracy",
                "Improvement",
                "ROC Gain",
                "Status",
            ]
            if col in raw.columns
        ]
        st.dataframe(raw[comparison_cols], hide_index=True, use_container_width=True)
    else:
        st.info("No benchmark comparison artifact is available.")

    fold_df = builtin_fold_results()
    st.subheader("Fold-by-Fold Results")
    if fold_df.empty:
        st.info("No built-in fold-by-fold artifact was found. Session model folds are shown below when available.")
    else:
        st.dataframe(fold_df, hide_index=True, use_container_width=True)

    st.subheader("Cross-Validation Summary")
    if not fold_df.empty:
        metric_cols = [col for col in ["Accuracy", "ROC-AUC", "accuracy", "roc_auc"] if col in fold_df.columns]
        drug_col = "Drug" if "Drug" in fold_df.columns else "drug"
        if drug_col in fold_df.columns and metric_cols:
            st.dataframe(fold_df.groupby(drug_col)[metric_cols].agg(["mean", "std"]).round(4), use_container_width=True)

    st.divider()
    st.subheader("Session Models")
    manager = get_model_manager()
    models = manager.list_models()
    if not models:
        st.info("No trained models are registered yet.")
        return

    rows = []
    for record in models:
        metrics = record.summary.get("metrics", {})
        rows.append(
            {
                "Model": record.drug_name,
                "Accuracy": metrics.get("accuracy"),
                "F1": metrics.get("f1"),
                "Precision": metrics.get("precision"),
                "Recall": metrics.get("recall"),
                "ROC": metrics.get("roc_auc"),
                "Cross-validation": metrics.get("cross_validation_score"),
                "Folds": metrics.get("folds"),
                "Validation samples": metrics.get("validation_dataset_size"),
                "Metric source": record.summary.get("metric_source"),
            }
        )
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    selected = st.selectbox(
        "Inspect session model",
        [record.model_id for record in models],
        format_func=lambda model_id: next(record.drug_name for record in models if record.model_id == model_id),
    )
    record = next(record for record in models if record.model_id == selected)
    cm = record.summary.get("metrics", {}).get("confusion_matrix")
    if cm:
        st.subheader("Confusion Matrix")
        st.dataframe(pd.DataFrame(cm), use_container_width=True)
    st.subheader("Training Configuration")
    st.json(record.summary.get("config", {}))
    fold_rows = record.summary.get("metrics", {}).get("fold_results", [])
    if fold_rows:
        st.subheader("Session Fold Results")
        st.dataframe(pd.DataFrame(fold_rows), hide_index=True, use_container_width=True)
