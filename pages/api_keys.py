from __future__ import annotations

import streamlit as st


def render_api_keys(client):

    st.title("🔑 API Keys")

    if not st.session_state.get("authenticated", False):
        st.warning("Please login first.")
        return

    # ----------------------------------------------------------
    # Load User Profile
    # ----------------------------------------------------------

    try:

        user = client.me()

        st.session_state.user = user

        api_key = (
            user.get("api_key")
            or st.session_state.get("api_key")
        )

        st.session_state.api_key = api_key

    except Exception as e:

        st.error(f"Unable to load API Key.\n\n{e}")

        return

    # ----------------------------------------------------------
    # Current API Key
    # ----------------------------------------------------------

    st.subheader("Current API Key")

    if api_key:

        st.text_input(
            "API Key",
            value=api_key,
            disabled=True,
        )

        st.code(api_key)

        st.caption(
            "Use this API key to authenticate external requests to the QUBE Predict REST API."
        )

    else:

        st.warning(
            "No API Key has been assigned to this account."
        )

    st.divider()

    # ----------------------------------------------------------
    # Example Usage
    # ----------------------------------------------------------

    st.subheader("Example")

    api_url = st.session_state.get(
        "api_url",
        "https://qube-predict-api.onrender.com",
    )

    example = f"""
curl -X POST "{api_url}/api/v1/predict" \\
-H "x-api-key: {api_key or 'YOUR_API_KEY'}" \\
-H "Content-Type: application/json" \\
-d '{{
  "drug":"Gemcitabine",
  "sample": {{
    "gene1": 0.42,
    "gene2": 1.81
  }}
}}'
"""

    st.code(example, language="bash")

    st.divider()

    # ----------------------------------------------------------
    # API Information
    # ----------------------------------------------------------

    st.subheader("API Details")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Authentication",
            "API Key",
        )

        st.metric(
            "Method",
            "POST",
        )

    with col2:

        st.metric(
            "Format",
            "JSON",
        )

        st.metric(
            "Version",
            "v1",
        )

    st.divider()

    st.subheader("Available Endpoints")

    endpoints = [
        ("POST", "/api/v1/predict"),
        ("POST", "/api/v1/predict/batch"),
        ("GET", "/api/v1/models"),
        ("GET", "/dashboard"),
        ("GET", "/billing/subscription"),
    ]

    for method, endpoint in endpoints:

        st.markdown(
            f"**{method}** `{endpoint}`"
        )

    st.divider()

    # ----------------------------------------------------------
    # Security Notes
    # ----------------------------------------------------------

    st.info(
        """
**Keep your API key secure.**

• Never commit it to GitHub.

• Never expose it inside frontend JavaScript.

• Rotate the key immediately if it is compromised.

• Use HTTPS for all production requests.
"""
    )

    # ----------------------------------------------------------
    # Future Feature
    # ----------------------------------------------------------

    st.subheader("Key Management")

    st.button(
        "🔄 Regenerate API Key (Coming Soon)",
        disabled=True,
        use_container_width=True,
    )

    st.caption(
        "Future versions will allow secure API key rotation."
    )