from __future__ import annotations

import streamlit as st
import pandas as pd


def render_usage(client):

    st.title("📊 Prediction Usage")

    if not st.session_state.get("authenticated", False):
        st.warning("Please login first.")
        return

    # ----------------------------------------------------------
    # Load dashboard data
    # ----------------------------------------------------------

    try:
        dashboard = client.dashboard()

    except Exception as e:
        st.error(f"Unable to load usage data.\n\n{e}")
        return

    usage = dashboard.get("usage", {})
    recent_predictions = dashboard.get("recent_predictions", [])

    used = usage.get("used", 0)
    limit = usage.get("limit", 0)
    remaining = usage.get("remaining", max(0, limit - used))
    percentage = usage.get("percentage", 0)

    # ----------------------------------------------------------
    # Usage Overview
    # ----------------------------------------------------------

    st.subheader("Monthly Prediction Usage")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Used",
            f"{used:,}",
        )

    with col2:
        st.metric(
            "Remaining",
            f"{remaining:,}",
        )

    with col3:
        st.metric(
            "Monthly Limit",
            f"{limit:,}",
        )

    with col4:
        st.metric(
            "Usage",
            f"{percentage:.1f}%",
        )

    st.progress(min(percentage / 100, 1.0))

    st.caption(
        f"{used:,} of {limit:,} predictions used this billing cycle."
    )

    st.divider()

    # ----------------------------------------------------------
    # Usage Breakdown
    # ----------------------------------------------------------

    st.subheader("Usage Summary")

    summary = pd.DataFrame(
        [
            {
                "Metric": "Predictions Used",
                "Value": used,
            },
            {
                "Metric": "Predictions Remaining",
                "Value": remaining,
            },
            {
                "Metric": "Monthly Limit",
                "Value": limit,
            },
            {
                "Metric": "Usage Percentage",
                "Value": f"{percentage:.1f}%",
            },
        ]
    )

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ----------------------------------------------------------
    # Recent Predictions
    # ----------------------------------------------------------

    st.subheader("Recent Prediction Activity")

    if not recent_predictions:

        st.info("No prediction activity recorded yet.")

        return

    rows = []

    for prediction in recent_predictions:

        rows.append(
            {
                "Drug": prediction.get("drug"),
                "Endpoint": prediction.get("endpoint"),
                "Success": "✅" if prediction.get("success") else "❌",
                "Created": prediction.get("created_at"),
            }
        )

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ----------------------------------------------------------
    # Usage Insights
    # ----------------------------------------------------------

    success_count = sum(
        1 for row in recent_predictions if row.get("success")
    )

    total = len(recent_predictions)

    success_rate = (
        (success_count / total) * 100
        if total > 0
        else 0
    )

    st.subheader("Insights")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Recent Success Rate",
            f"{success_rate:.1f}%",
        )

    with col2:

        if percentage < 50:

            st.success("Usage is well within your monthly quota.")

        elif percentage < 80:

            st.warning("You are approaching your monthly limit.")

        else:

            st.error("High usage detected. Consider upgrading your plan.")