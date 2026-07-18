from __future__ import annotations

import pandas as pd
import streamlit as st


def render_batch_prediction(client):

    st.title("📊 Batch Prediction")
    st.caption(
        "Run predictions for multiple biological samples using trained QUBE Predict models."
    )

    st.markdown("---")

    # ==========================================================
    # LOAD AVAILABLE MODELS
    # ==========================================================

    try:

        models_response = client.models()

        models = models_response.get("models", [])

        drug_names = []

        for model in models:

            if isinstance(model, dict):

                drug = (
                    model.get("drug")
                    or model.get("name")
                    or model.get("model_name")
                )

                if drug:
                    drug_names.append(drug)

            elif isinstance(model, str):

                drug_names.append(model)

        drug_names = sorted(list(set(drug_names)))

        if not drug_names:

            st.warning("No trained models are currently available.")

            st.stop()

    except Exception as e:

        st.error(f"Unable to load trained models.\n\n{e}")

        st.stop()

    # ==========================================================
    # MODEL INFO
    # ==========================================================

    st.metric(
        "🧬 Models Available",
        len(drug_names),
    )

    drug = st.selectbox(
        "Prediction Model",
        drug_names,
    )

    st.markdown("---")

    # ==========================================================
    # CSV UPLOAD
    # ==========================================================

    uploaded_file = st.file_uploader(
        "Upload CSV Dataset",
        type=["csv"],
        help="Upload a CSV containing one biological sample per row.",
    )

    if uploaded_file is not None:

        try:

            df = pd.read_csv(uploaded_file)

            st.success(f"Loaded {len(df)} samples.")

            with st.expander("Preview Dataset", expanded=True):

                st.dataframe(
                    df.head(10),
                    use_container_width=True,
                )

        except Exception as e:

            st.error(f"Unable to read CSV.\n\n{e}")

            return

        st.markdown("")

        if st.button(
            "🚀 Run Batch Prediction",
            use_container_width=True,
        ):

            try:

                uploaded_file.seek(0)

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        "text/csv",
                    )
                }

                with st.spinner("Running predictions..."):

                    result = client.batch_predict(
                        drug,
                        files,
                    )

                results = result.get(
                    "results",
                    [],
                )

                if not results:

                    st.warning("No predictions returned.")

                    return

                results_df = pd.DataFrame(results)

                st.success(
                    f"Successfully processed {len(results_df)} samples."
                )

                st.dataframe(
                    results_df,
                    use_container_width=True,
                )

                csv = results_df.to_csv(
                    index=False,
                ).encode("utf-8")

                st.download_button(
                    "⬇ Download Prediction Results",
                    csv,
                    file_name="batch_predictions.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            except Exception as e:

                st.error(str(e))

    # ==========================================================
    # SAMPLE FORMAT
    # ==========================================================

    st.markdown("---")

    st.subheader("Sample CSV Format")

    example = pd.DataFrame(
        {
            "TP53": [2.3, 1.7, 4.1],
            "KRAS": [1.1, 0.9, 2.4],
            "EGFR": [3.9, 2.5, 5.2],
        }
    )

    st.dataframe(
        example,
        use_container_width=True,
    )

    csv = example.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Sample Dataset",
        csv,
        file_name="sample_dataset.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.info(
        """
Each row represents one biological sample.

Workflow:

1. Select a trained prediction model.
2. Upload your CSV dataset.
3. Run batch prediction.
4. Review prediction results.
5. Download the generated predictions.
"""
    )