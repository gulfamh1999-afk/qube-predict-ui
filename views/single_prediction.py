from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def _extract_model_names(payload: Any) -> list[str]:
    """
    Accepts either:
    - ["DrugA", "DrugB"]
    - {"models": [...]}
    """

    if isinstance(payload, list):
        models = payload
    elif isinstance(payload, dict):
        models = payload.get("models", [])
    else:
        return []

    names = []

    for model in models:

        if isinstance(model, str):
            names.append(model)

        elif isinstance(model, dict):

            name = (
                model.get("drug")
                or model.get("drug_name")
                or model.get("name")
                or model.get("model")
            )

            if name:
                names.append(str(name))

    return sorted(names)


def _sample_from_csv(dataframe: pd.DataFrame) -> dict[str, Any]:

    if dataframe.empty:
        raise ValueError(
            "Uploaded CSV does not contain any samples."
        )

    if {"gene_name", "value"}.issubset(dataframe.columns):

        sample = (
            dataframe
            .set_index("gene_name")["value"]
            .to_dict()
        )

    elif {"gene", "value"}.issubset(dataframe.columns):

        sample = (
            dataframe
            .set_index("gene")["value"]
            .to_dict()
        )

    else:

        sample = dataframe.iloc[0].to_dict()

    sample.pop("sample_id", None)

    return {
        str(gene): value
        for gene, value in sample.items()
        if pd.notna(value)
    }


def render_single_prediction(client):

    st.title("🧬 Single Prediction")

    if not st.session_state.get("authenticated", False):
        st.warning("Please login first.")
        return

    # --------------------------------------------------
    # Load Models
    # --------------------------------------------------

    try:

        models = _extract_model_names(
            client.models()
        )

    except Exception as e:

        st.error(f"Unable to load models.\n\n{e}")

        return

    if not models:

        st.warning("No prediction models are available.")

        return

    selected_drug = st.selectbox(
        "Drug",
        models,
    )

    uploaded_file = st.file_uploader(
        "Gene Expression CSV",
        type=["csv"],
    )

    if uploaded_file is None:
        return

    try:

        dataframe = pd.read_csv(uploaded_file)

    except Exception as e:

        st.error(f"Unable to read CSV.\n\n{e}")

        return

    st.dataframe(
        dataframe.head(),
        use_container_width=True,
    )

    if st.button(
        "Run Prediction",
        type="primary",
        use_container_width=True,
    ):

        try:

            sample = _sample_from_csv(
                dataframe
            )

        except Exception as e:

            st.error(str(e))

            return

        with st.spinner(
            "Running prediction..."
        ):

            try:

                result = client.predict(
                    drug=selected_drug,
                    sample=sample,
                )

            except Exception as e:

                st.error(
                    f"Prediction failed.\n\n{e}"
                )

                return

        st.success("Prediction completed.")

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Prediction",
                result.get(
                    "prediction",
                    "-",
                ),
            )

        with col2:

            st.metric(
                "Probability",
                result.get(
                    "probability",
                    "-",
                ),
            )

        with col3:

            st.metric(
                "Confidence",
                result.get(
                    "confidence",
                    "-",
                ),
            )

        st.divider()

        st.subheader("Raw API Response")

        st.json(result)