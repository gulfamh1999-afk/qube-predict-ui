from __future__ import annotations

import streamlit as st

from backend.state import initialize_state
from backend.api_client import ApiClient

from ui.theme import apply_theme, render_sidebar

# ==========================================================
# PUBLIC PAGES
# ==========================================================

from pages.login import render_login
from pages.signup import render_signup
from pages.logout import render_logout

# ==========================================================
# APPLICATION PAGES
# ==========================================================

from pages.profile import render_profile
from pages.billing import render_billing
from pages.billing_history import render_billing_history
from pages.usage import render_usage
from pages.api_keys import render_api_keys

from pages.single_prediction import render_single_prediction
from pages.about import render_about


# ==========================================================
# PAGE REGISTRY
# ==========================================================

PUBLIC_PAGES = {
    "Login": render_login,
    "Signup": render_signup,
}

PRIVATE_PAGES = {
    "Single Prediction": render_single_prediction,
    "Usage": render_usage,
    "Billing": render_billing,
    "Billing History": render_billing_history,
    "API Keys": render_api_keys,
    "Profile": render_profile,
    "About": render_about,
    "Logout": render_logout,
}

# ==========================================================
# INITIALIZATION
# ==========================================================

def initialize_application():

    initialize_state()

    defaults = {
        "api_url": "https://qube-predict-api.onrender.com",
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

    if st.session_state.authenticated:

        pages = list(PRIVATE_PAGES.keys())

    else:

        pages = list(PUBLIC_PAGES.keys())

    return render_sidebar(pages)


# ==========================================================
# PAGE DISPATCH
# ==========================================================

def render_page(page: str, client: ApiClient):

    if page in PUBLIC_PAGES:

        PUBLIC_PAGES[page](client)
        return

    if not st.session_state.authenticated:

        st.session_state.page = "Login"
        st.rerun()

    PRIVATE_PAGES[page](client)


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

    st.session_state.page = page

    try:

        render_page(page, client)

    except Exception as e:

        st.error("Application Error")

        with st.expander("Technical Details"):

            st.exception(e)


# ==========================================================
# ENTRY
# ==========================================================

if __name__ == "__main__":

    main()