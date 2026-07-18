from __future__ import annotations

import streamlit as st


def render_refund_policy(client=None):

    st.title("💳 Refund Policy")

    st.caption("Last Updated: July 2026")

    st.markdown("""
## Subscription Plans

QUBE Predict offers monthly subscriptions.

---

## Cancellation

Subscriptions may be cancelled at any time.

Cancellation prevents future billing.

---

## Refunds

Payments already processed are generally non-refundable.

If duplicate billing or payment errors occur,
please contact support.

---

## Failed Payments

Failed or cancelled transactions
are automatically handled by Razorpay.

---

## Contact

sales@qubepredict.ai
""")