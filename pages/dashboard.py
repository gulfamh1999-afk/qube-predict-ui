from __future__ import annotations

import streamlit as st


def render_dashboard(client):
    st.title("📊 Dashboard")

    if not st.session_state.get("authenticated", False):
        st.warning("Please login first.")
        return

    # -----------------------------------------
    # User
    # -----------------------------------------

    try:
        user = client.me()
    except Exception as e:
        st.error(f"Unable to load profile.\n\n{e}")
        return

    # -----------------------------------------
    # Dashboard
    # -----------------------------------------

    try:
        dashboard = client.dashboard()
    except Exception:
        dashboard = {}

    # -----------------------------------------
    # Subscription
    # -----------------------------------------

    try:
        subscription = client.subscription()
    except Exception:
        subscription = {}

    st.success("🟢 Connected to QUBE Predict Cloud")

    st.write(
        f"Welcome **{user.get('full_name', user.get('email'))}**"
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Plan",
            subscription.get("plan", "Free"),
        )

    with col2:
        st.metric(
            "Status",
            subscription.get("status", "Inactive"),
        )

    with col3:
        st.metric(
            "Predictions Used",
            dashboard.get("predictions_used", 0),
        )

    with col4:
        st.metric(
            "Remaining",
            dashboard.get("remaining_predictions", 0),
        )

    st.divider()

    st.subheader("API")

    api_url = st.session_state.get(
        "api_url",
        "https://qube-predict.onrender.com",
    )

    st.code(api_url)

    st.divider()

    st.subheader("System")

    st.write("Backend Status: 🟢 Online")

    st.write("Authentication: JWT")

    st.write("Deployment: Render")

    st.write("Frontend: Streamlit")

    st.divider()

    st.subheader("Recent Activity")

    history = dashboard.get("recent_predictions", [])

    if history:
        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No predictions yet.")