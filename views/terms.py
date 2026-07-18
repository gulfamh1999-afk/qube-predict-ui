from __future__ import annotations

import streamlit as st


def render_terms(client=None):

    st.title("📜 Terms & Conditions")

    st.caption("Last Updated: July 2026")

    st.markdown("""
## Acceptance

By using QUBE Predict you agree to these Terms.

---

## Service

QUBE Predict provides cloud-based AI drug response prediction.

---

## Accounts

You are responsible for maintaining
the confidentiality of your login credentials.

---

## API Usage

API Keys are personal.

Sharing or reselling API access is prohibited.

---

## Intellectual Property

QUBE Predict,
QUBE Engine,
algorithms,
models,
documentation,
and software remain the intellectual property
of QUBE Predict.

---

## Limitation of Liability

Predictions are intended for research purposes.

Users remain responsible for interpretation
and downstream decisions.

---

## Changes

These Terms may be updated periodically.
""")