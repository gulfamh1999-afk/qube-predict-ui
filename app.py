from __future__ import annotations

import streamlit as st

from backend.state import initialize_state
from backend.api_client import ApiClient

from ui.theme import apply_theme, render_sidebar

# ==========================================================
# PUBLIC PAGES
# ==========================================================


# ==========================================================
# PRIVATE PAGES
# ==========================================================

from views.login import render_login
from views.signup import render_signup
from views.logout import render_logout

from views.dashboard import render_dashboard
from views.profile import render_profile
from views.billing import render_billing
from views.billing_history import render_billing_history
from views.usage import render_usage
from views.api_keys import render_api_keys
from views.single_prediction import render_single_prediction
from views.batch_prediction import render_batch_prediction
from views.about import render_about
from views.privacy_policy import render_privacy_policy
from views.terms import render_terms
from views.refund_policy import render_refund_policy
from views.contact import render_contact


# ==========================================================
# PAGE REGISTRY
# ==========================================================

PUBLIC_PAGES = {
    "Login": render_login,
    "Signup": render_signup,
}

PRIVATE_PAGES = {
    "Dashboard": render_dashboard,
    "Single Prediction": render_single_prediction,
    "Batch Prediction": render_batch_prediction,
    "Usage": render_usage,
    "Billing": render_billing,
    "Billing History": render_billing_history,
    "API Keys": render_api_keys,
    "Profile": render_profile,
    "About": render_about,
    "Logout": render_logout,
    "Privacy Policy": render_privacy_policy,
    "Terms & Conditions": render_terms,
    "Refund Policy": render_refund_policy,
    "Contact": render_contact,
}

# ==========================================================
# INITIALIZATION
# ==========================================================


def initialize_application():

    initialize_state()

    defaults = {
        "api_url": "https://qube-predict.onrender.com",
        "authenticated": False,
        "jwt": None,
        "refresh_token": None,
        "api_key": None,
        "user": None,
        "page": "Login",
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


# ==========================================================
# SIDEBAR
# ==========================================================


def build_navigation():

    if st.session_state.get("authenticated", False):
        pages = list(PRIVATE_PAGES.keys())
    else:
        pages = list(PUBLIC_PAGES.keys())

    page = render_sidebar(pages)

    if page not in pages:
        page = pages[0]

    return page


# ==========================================================
# PAGE DISPATCH
# ==========================================================


def render_page(page: str, client: ApiClient):

    if page in PUBLIC_PAGES:
        PUBLIC_PAGES[page](client)
        return

    if not st.session_state.get("authenticated", False):
        render_login(client)
        return

    renderer = PRIVATE_PAGES.get(page)

    if renderer is None:
        st.error(f"Unknown page: {page}")
        return

    renderer(client)


# ==========================================================
# MAIN
# ==========================================================


def main():

    st.set_page_config(
        page_title="QUBE Predict",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_theme()

    initialize_application()

    client = ApiClient()

    page = build_navigation()

    try:

        render_page(page, client)

    except Exception as e:

        st.error("An unexpected application error occurred.")

        with st.expander("Technical Details"):
            st.exception(e)


# ==========================================================
# ENTRY
# ==========================================================

if __name__ == "__main__":
    main()