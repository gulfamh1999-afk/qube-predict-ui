from __future__ import annotations

import streamlit as st


def render_privacy_policy(client=None):

    st.title("🔒 Privacy Policy")

    st.caption("Last Updated: July 2026")

    st.markdown("""
## Overview

QUBE Predict is committed to protecting your privacy.

This Privacy Policy explains what information we collect,
how it is used, and how it is protected.

---

## Information We Collect

We may collect:

- Name
- Email address
- Company
- Country
- Uploaded gene expression datasets
- API usage statistics
- Billing information processed through Razorpay

---

## Uploaded Data

Gene expression files uploaded for prediction are processed
only to generate prediction results.

Uploaded files are not sold or shared with third parties.

---

## Payments

Payments are securely processed by Razorpay.

QUBE Predict never stores your card or banking information.

---

## Security

We use encrypted HTTPS connections,
JWT authentication,
API Keys,
and secure cloud infrastructure.

---

## Data Deletion

You may request deletion of your account
and associated personal data by contacting support.

---

## Contact

sales@qubepredict.ai
""")