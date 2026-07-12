from __future__ import annotations

import streamlit as st


def render_about() -> None:
    st.title("About QUBE2")
    st.markdown(
        """
        QUBE2 is a graph-based drug response prediction engine that represents genes as an
        interaction graph, expands samples into topology, spatial, spectral and quantum-inspired
        descriptor banks, selects a compact descriptor set, and trains a Random Forest backend.

        The Streamlit application is an interface layer only. It imports the validated engine,
        uses its callable classifier and reports, and leaves graph construction, descriptor
        generation, feature selection, cross validation and prediction logic unchanged.
        """
    )
    st.subheader("Methodology")
    st.write("Graph representation: correlation or supplied pathway edge-list over gene features.")
    st.write("Spatial descriptors: graph diffusion neighborhoods and feature-field interactions.")
    st.write("Descriptor bank: expanded graph descriptors reduced to selected informative features.")
    st.write("Backend: balanced Random Forest classifier.")
    st.write("Validation: fold-contained representation fitting with leakage sanity controls.")
