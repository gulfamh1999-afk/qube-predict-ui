from __future__ import annotations

import streamlit as st


def render_about(client):
    st.title("🧬 About QUBE Predict")

    st.markdown(
        """
        **QUBE Predict** is a cloud-based AI platform for drug response prediction.

        The platform combines graph-based feature engineering with machine learning
        to predict therapeutic response from molecular data. Predictions are served
        through a secure REST API and accessed via this Streamlit web application.

        This frontend acts solely as a client application. All authentication,
        prediction, billing, user management, and API operations are performed by
        the QUBE Predict backend.
        """
    )

    st.subheader("Platform Architecture")

    st.markdown(
        """
        - **Frontend:** Streamlit
        - **Backend:** FastAPI
        - **Authentication:** JWT
        - **Database:** PostgreSQL
        - **Deployment:** Render Cloud
        - **API:** RESTful HTTPS
        """
    )

    st.subheader("Prediction Engine")

    st.write(
        """
        The QUBE engine represents biological data as graph-based descriptors,
        generates engineered feature representations, and performs prediction
        using trained machine learning models deployed on the backend.
        """
    )

    st.subheader("Features")

    st.markdown(
        """
        - Secure user authentication
        - Cloud-based prediction API
        - API key management
        - Subscription and billing
        - Usage monitoring
        - Drug response prediction
        """
    )

    st.subheader("Version")

    st.info("QUBE Predict Cloud v3.1")