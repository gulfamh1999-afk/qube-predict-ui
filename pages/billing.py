from __future__ import annotations

import streamlit as st


def render_billing(client):

    st.title("💳 Subscription & Billing")

    if not st.session_state.get("authenticated", False):
        st.warning("Please login first.")
        return

    # ----------------------------------------------------------
    # Load current subscription
    # ----------------------------------------------------------

    try:
        subscription = client.subscription()
    except Exception:
        subscription = {
            "plan": "Free",
            "status": "inactive",
        }

    # ----------------------------------------------------------
    # Load available plans
    # ----------------------------------------------------------

    try:
        plans = client.plans()
    except Exception as e:
        st.error(f"Unable to load plans.\n\n{e}")
        return

    # ----------------------------------------------------------
    # Current Subscription
    # ----------------------------------------------------------

    st.subheader("Current Subscription")

    col1, col2, col3 = st.columns(3)

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
        renewal = subscription.get("renewal_date")

        if renewal:
            st.metric("Renewal", renewal[:10])
        else:
            st.metric("Renewal", "--")

    st.divider()

    # ----------------------------------------------------------
    # Available Plans
    # ----------------------------------------------------------

    st.subheader("Available Plans")

    cols = st.columns(len(plans))

    for index, (plan_name, plan) in enumerate(plans.items()):

        with cols[index]:

            st.markdown(f"### {plan_name}")

            if "price" in plan:
                st.metric(
                    "Price",
                    f"₹{plan['price']:,}/month",
                )

            if "predictions" in plan:
                st.metric(
                    "Predictions",
                    f"{plan['predictions']:,}",
                )

            if "contact" in plan:
                st.info(plan["contact"])

            if plan_name != "Enterprise":

                if st.button(
                    f"Subscribe to {plan_name}",
                    key=f"subscribe_{plan_name}",
                    use_container_width=True,
                ):

                    try:

                        result = client.create_subscription(
                            plan_name
                        )

                        st.success(
                            "Subscription created successfully."
                        )

                        if result.get("razorpay_short_url"):

                            st.link_button(
                                "Proceed to Razorpay Checkout",
                                result["razorpay_short_url"],
                                use_container_width=True,
                            )

                        else:

                            st.warning(
                                "No Razorpay checkout URL returned."
                            )

                    except Exception as e:

                        st.error(str(e))

    st.divider()

    # ----------------------------------------------------------
    # Cancel Subscription
    # ----------------------------------------------------------

    if (
        subscription.get("status", "").lower() == "active"
        or subscription.get("active") is True
    ):

        st.subheader("Manage Subscription")

        st.warning(
            "Cancelling your subscription will keep it active "
            "until the current billing period ends."
        )

        if st.button(
            "Cancel Subscription",
            type="primary",
            use_container_width=True,
        ):

            try:

                result = client.cancel_subscription()

                st.success(
                    result.get(
                        "message",
                        "Subscription cancelled."
                    )
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))