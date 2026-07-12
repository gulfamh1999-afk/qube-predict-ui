from __future__ import annotations

import streamlit as st


def initialize_state() -> None:
    defaults = {
        "last_predictions": None,
        "last_prediction_report": None,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)