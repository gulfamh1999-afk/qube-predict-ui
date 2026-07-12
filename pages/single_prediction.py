from __future__ import annotations

from typing import Any

import pandas as pd
import requests
import streamlit as st


def _api_base_url() -> str:
    return st.session_state.get("api_url", "").rstrip("/")


def _api_headers() -> dict[str, str]:
    return {
        "x-api-key": st.session_state.get("api_key", ""),
        "Content-Type": "application/json",
    }


def _extract_model_names(payload: dict[str, Any]) -> list[str]:
    models = payload.get("models", [])
    names: list[str] = []

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


def _fetch_models() -> list[str]:
    api_url = _api_base_url()
    api_key = st.session_state.get("api_key", "")

    if not api_url:
        st.error("API URL is not configured.")
        return []

    if not api_key:
        st.error("API key is required.")
        return []

    try:
        response = requests.get(
            f"{api_url}/api/v1/models",
            headers={"x-api-key": api_key},
            timeout=30,
        )
    except requests.RequestException as exc:
        st.error(f"Could not load available models: {exc}")
        return []

    if not response.ok:
        st.error(_api_error(response, "Could not load available models."))
        return []

    try:
        return _extract_model_names(response.json())
    except ValueError:
        st.error("Could not load available models: invalid API response.")
        return []


def _api_error(response: requests.Response, fallback: str) -> str:
    try:
        detail = response.json().get("detail")
    except ValueError:
        detail = response.text

    if detail:
        return f"{fallback} {detail}"

    return fallback


def _sample_from_csv(dataframe: pd.DataFrame) -> dict[str, Any]:
    if dataframe.empty:
        raise ValueError("Uploaded CSV does not contain any samples.")

    if {"gene_name", "value"}.issubset(dataframe.columns):
        sample = dataframe.set_index("gene_name")["value"].to_dict()
    elif {"gene", "value"}.issubset(dataframe.columns):
        sample = dataframe.set_index("gene")["value"].to_dict()
    else:
        sample = dataframe.iloc[0].to_dict()

    sample.pop("sample_id", None)
    return {
        str(gene): value
        for gene, value in sample.items()
        if pd.notna(value)
    }


def render_single_prediction() -> None:
    st.subheader("Single Prediction")

    models = _fetch_models()
    selected_drug = st.selectbox(
        "Drug",
        options=models,
        disabled=not models,
    )

    uploaded_file = st.file_uploader(
        "Gene-expression CSV",
        type=["csv"],
    )

    if uploaded_file is None:
        return

    try:
        dataframe = pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")
        return

    if st.button("Predict", disabled=not selected_drug):
        try:
            sample = _sample_from_csv(dataframe)
        except ValueError as exc:
            st.error(str(exc))
            return

        payload = {
            "drug": selected_drug,
            "sample": sample,
        }

        with st.spinner("Running prediction..."):
            try:
                response = requests.post(
                    f"{_api_base_url()}/api/v1/predict",
                    json=payload,
                    headers=_api_headers(),
                    timeout=60,
                )
            except requests.RequestException as exc:
                st.error(f"Prediction failed: {exc}")
                return

        if not response.ok:
            st.error(_api_error(response, "Prediction failed."))
            return

        try:
            result = response.json()
        except ValueError:
            st.error("Prediction failed: invalid API response.")
            return

        st.metric("Prediction", result.get("prediction"))
        st.metric("Probability", result.get("probability"))
        st.metric("Confidence", result.get("confidence"))


def render() -> None:
    render_single_prediction()