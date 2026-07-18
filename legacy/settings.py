from __future__ import annotations

import streamlit as st

from backend.data import inspect_uploaded_dataset
from backend.model_manager import ManagedModel, get_model_manager
from backend.navigation import navigate_to
from backend.qube_wrapper import train_from_upload


def render_settings() -> None:
    st.title("Settings")
    st.caption("Load saved QUBE2 models or train a session model from a labelled dataset.")
    manager = get_model_manager()

    saved = manager.list_models()
    if saved:
        selected = st.selectbox(
            "Saved model",
            [record.model_id for record in saved],
            format_func=lambda model_id: next(record.drug_name for record in saved if record.model_id == model_id),
            help="Choose a QUBE2 model previously saved in the models folder. Loading a model lets you predict immediately without retraining.",
        )
        if st.button(
            "Load saved model",
            use_container_width=True,
            help="Loads the selected model, feature list, training summary, and QUBE2 diagnostics into the active session.",
        ):
            try:
                record = manager.load_model(selected)
                st.success(f"Loaded {record.drug_name}.")
            except Exception as exc:
                st.error(f"Could not load the saved model: {exc}")
    else:
        st.info("No saved models found in models/. Train one below or use a session-only model.")

    st.divider()
    st.subheader("Train Interface Model")
    mode = st.segmented_control(
        "Training mode",
        ["Drug response", "Target labelled"],
        default="Drug response",
        help="Drug response mode expects CCLE/GDSC-style columns. Target labelled mode uses any numeric feature table with one label column.",
    )
    uploaded = st.file_uploader(
        "Labelled CSV/XLSX",
        type=["csv", "xlsx", "xls"],
        help="Upload training data here. For drug mode include DRUG_NAME, LN_IC50, and numeric gene-expression columns. For target mode include numeric features plus the label column.",
    )
    drug = None
    target = None
    inspection = None
    valid_training_input = uploaded is not None

    if mode == "Drug response":
        if uploaded is not None:
            try:
                inspection = inspect_uploaded_dataset(uploaded)
                _render_upload_summary(inspection)
            except Exception as exc:
                st.error(f"Could not inspect the uploaded dataset: {exc}")
                valid_training_input = False

        if inspection and inspection["has_drug_name"]:
            detected_drugs = inspection["drugs"]
            if len(detected_drugs) == 1:
                drug = detected_drugs[0]
                st.success(f"Detected one drug in the dataset: {drug}")
            elif detected_drugs:
                previous = st.session_state.get("training_drug")
                if previous and previous not in detected_drugs:
                    st.warning(
                        f"'{previous}' is not present in this upload. Select one of the detected drugs below."
                    )
                default_index = detected_drugs.index(previous) if previous in detected_drugs else 0
                drug = st.selectbox(
                    "Drug",
                    detected_drugs,
                    index=default_index,
                    key="training_drug",
                    format_func=lambda value: f"{value} ({inspection['drug_counts'][value]:,} samples)",
                    help="Detected from the uploaded DRUG_NAME column. QUBE2 filters the dataset to this drug before training.",
                )
            else:
                st.warning("The DRUG_NAME column is present, but no usable drug names were found.")
                valid_training_input = False
        elif uploaded is not None:
            st.warning("Drug response training needs a DRUG_NAME column. Upload a CCLE/GDSC-style dataset or switch to Target labelled mode.")
            valid_training_input = False
        else:
            st.info("Upload a labelled dataset to detect available drugs.")
            valid_training_input = False

        if inspection and "LN_IC50" not in inspection["found_required"]:
            st.warning("LN_IC50 is missing. Drug response training needs LN_IC50 for the median response split.")
            valid_training_input = False
        if inspection and inspection["features"] == 0:
            st.warning("No numeric gene-expression feature columns were detected.")
            valid_training_input = False

        st.caption("Requires DRUG_NAME, LN_IC50, and numeric gene-expression columns.")
    else:
        target = st.text_input(
            "Target column",
            value="label",
            help="Name of the column containing class labels. All other numeric columns are treated as model features.",
        )
        if uploaded is not None:
            try:
                inspection = inspect_uploaded_dataset(uploaded, target=target)
                _render_upload_summary(inspection, target=target)
                if target not in inspection.get("found_required", []) and not inspection["target_present"]:
                    st.warning(f"Target column '{target}' was not found in this upload.")
                    valid_training_input = False
                if inspection["features"] == 0:
                    st.warning("No numeric feature columns were detected.")
                    valid_training_input = False
            except Exception as exc:
                st.error(f"Could not inspect the uploaded dataset: {exc}")
                valid_training_input = False
        else:
            valid_training_input = False

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        n_descriptors = st.number_input(
            "Selected descriptors",
            16,
            1024,
            256,
            step=16,
            help="Number of graph descriptor features kept after QUBE2 feature selection. The validated default is 256.",
        )
    with col_b:
        rf_trees = st.number_input(
            "RF trees",
            100,
            1200,
            600,
            step=50,
            help="Number of trees in the Random Forest backend. Higher values can improve stability but train slower.",
        )
    with col_c:
        persist = st.checkbox(
            "Save model",
            value=False,
            help="Save the trained model under models/ so it can be loaded instantly later.",
        )

    save_as = (
        st.text_input(
            "Save as",
            value=(drug or target or "qube_model"),
            help="File-safe model name. The app stores model.pkl, descriptor_bank.pkl, config.json, metrics.json, and training_report.json under models/<name>/.",
        )
        if persist
        else None
    )

    if st.button(
        "Train QUBE2 model",
        use_container_width=True,
        disabled=not valid_training_input or (mode == "Drug response" and not drug),
        help="Runs the frozen QUBE2 graph descriptor pipeline and trains the Random Forest model on the uploaded labelled data.",
    ):
        try:
            with st.spinner("QUBE2 graph descriptors and Random Forest are fitting..."):
                model, feature_names, summary = train_from_upload(
                    uploaded,
                    mode=mode,
                    drug=drug,
                    target=target,
                    n_descriptors=int(n_descriptors),
                    rf_trees=int(rf_trees),
                )
            record = manager.register_model(
                model=model,
                feature_names=feature_names,
                summary=summary,
                diagnostics=model.report(),
                persist=persist,
                name=save_as or drug or target,
            )
            st.session_state.rendered_training_complete = record.model_id
            _render_training_complete(manager, record)
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Training could not be completed: {exc}")

    last_id = st.session_state.get("last_training_model_id")
    if (
        last_id
        and last_id in st.session_state.get("models", {})
        and st.session_state.get("rendered_training_complete") != last_id
    ):
        _render_training_complete(manager, st.session_state.models[last_id], compact=True)


def _render_upload_summary(inspection: dict, target: str | None = None) -> None:
    if target:
        found = [target] if inspection["target_present"] else []
        missing = [] if inspection["target_present"] else [target]
    else:
        found = inspection["found_required"]
        missing = inspection["missing_required"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Samples", f"{inspection['samples']:,}", help="Rows detected in the uploaded dataset.")
    c2.metric("Features", f"{inspection['features']:,}", help="Estimated numeric feature columns, excluding known metadata.")
    c3.metric("Detected drug(s)", f"{len(inspection['drugs']):,}", help="Unique values detected in the DRUG_NAME column.")
    c4.metric(
        "Required columns",
        f"{len(found)} found / {len(missing)} missing",
        help="Columns required for the selected workflow.",
    )

    if inspection["drug_counts"]:
        with st.expander("Detected drugs and sample counts", expanded=len(inspection["drug_counts"]) <= 8):
            st.dataframe(
                [{"Drug": drug, "Samples": count} for drug, count in inspection["drug_counts"].items()],
                hide_index=True,
                use_container_width=True,
            )

    if found:
        st.success("Required columns found: " + ", ".join(found))
    if missing:
        st.warning("Required columns missing: " + ", ".join(missing))


def _render_training_complete(manager, record: ManagedModel, *, compact: bool = False) -> None:
    metrics = record.summary.get("metrics", {})
    st.success("Training Complete")
    if not compact:
        st.balloons()

    cols = st.columns(4)
    cols[0].metric("Drug", record.drug_name)
    cols[1].metric("Samples", record.summary.get("samples", "NA"))
    cols[2].metric("Descriptors", record.summary.get("selected_descriptors", "NA"))
    cols[3].metric("RF Trees", record.summary.get("rf_trees", "NA"))

    metric_cols = st.columns(5)
    metric_cols[0].metric("CV Accuracy", _fmt(metrics.get("accuracy")))
    metric_cols[1].metric("Precision", _fmt(metrics.get("precision")))
    metric_cols[2].metric("Recall", _fmt(metrics.get("recall")))
    metric_cols[3].metric("F1", _fmt(metrics.get("f1")))
    metric_cols[4].metric("ROC", _fmt(metrics.get("roc_auc")))

    st.write(f"Validation method: {metrics.get('validation_method', 'NA')}")
    st.write(f"Training time: {record.summary.get('training_time', 0):.2f}s")
    st.write(f"Save location: {record.model_path or 'Session only'}")

    c1, c2, c3 = st.columns(3)
    if c1.button("Open Model", key=f"open_model_{record.model_id}", use_container_width=True):
        manager.load_model(record.model_id)
        navigate_to("Models")
        st.rerun()
    if c2.button("Predict", key=f"predict_model_{record.model_id}", use_container_width=True):
        manager.load_model(record.model_id)
        navigate_to("Single Prediction")
        st.rerun()
    c3.download_button(
        "Export Report",
        data=manager.export_pdf(record),
        file_name=f"{record.model_id}_model_report.pdf",
        mime="application/pdf",
        key=f"export_report_{record.model_id}",
        use_container_width=True,
    )


def _fmt(value) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)
