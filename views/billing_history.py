from __future__ import annotations

import pandas as pd
import streamlit as st


def render_billing_history(client):
    st.title("🧾 Billing History")

    if not st.session_state.get("authenticated", False):
        st.warning("Please login first.")
        return

    # ----------------------------------------------------------
    # Load Billing History
    # ----------------------------------------------------------

    try:
        payments = client.billing_history()
    except Exception as e:
        st.error(f"Unable to load billing history.\n\n{e}")
        return

    if not payments:
        st.info("No payments have been recorded yet.")
        return

    # ----------------------------------------------------------
    # Summary Metrics
    # ----------------------------------------------------------

    total_paid = sum(
        (payment.get("amount") or 0)
        for payment in payments
    )

    total_transactions = len(payments)

    successful = sum(
        1
        for payment in payments
        if payment.get("status", "").lower() == "captured"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Payments", total_transactions)

    with col2:
        st.metric("Successful", successful)

    with col3:
        st.metric(
            "Total Paid",
            f"₹{total_paid:,.2f}",
        )

    st.divider()

    # ----------------------------------------------------------
    # Billing Table
    # ----------------------------------------------------------

    rows = []

    for payment in payments:

        rows.append(
            {
                "Date": payment.get("paid_at")
                or payment.get("created_at")
                or "-",

                "Amount": f"₹{(payment.get('amount') or 0):,.2f}",

                "Currency": payment.get(
                    "currency",
                    "INR",
                ),

                "Status": payment.get(
                    "status",
                    "-",
                ).title(),

                "Payment ID": payment.get(
                    "razorpay_payment_id",
                    "-",
                ),

                "Invoice": payment.get(
                    "invoice_url",
                    "-",
                ),
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
    # Payment Details
    # ----------------------------------------------------------

    st.subheader("Payment Details")

    for payment in payments:

        amount = payment.get("amount") or 0

        status = payment.get(
            "status",
            "Unknown",
        ).title()

        paid_at = (
            payment.get("paid_at")
            or payment.get("created_at")
            or "-"
        )

        with st.expander(
            f"₹{amount:,.2f} • {status} • {paid_at}"
        ):

            st.write(
                f"**Payment ID:** {payment.get('razorpay_payment_id', '-')}"
            )

            st.write(
                f"**Amount:** ₹{amount:,.2f}"
            )

            st.write(
                f"**Currency:** {payment.get('currency', 'INR')}"
            )

            st.write(
                f"**Status:** {status}"
            )

            st.write(
                f"**Paid At:** {paid_at}"
            )

            invoice = payment.get("invoice_url")

            if invoice:
                st.link_button(
                    "Open Invoice",
                    invoice,
                    use_container_width=True,
                )