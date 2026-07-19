"""Production Streamlit shell for QUBE Predict."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from components.qube_ui import apply_enterprise_theme, esc, footer, status_pill
from pages.about import render_about
from pages.admin import render_admin
from pages.batch_prediction import render_batch_prediction
from pages.billing_history import render_billing_history
from pages.dashboard import render_dashboard
from pages.drug_library import render_drug_library
from pages.login import render_login_page
from pages.model_diagnostics import render_model_diagnostics
from pages.models import render_models
from pages.policies import render_contact, render_privacy_policy, render_refund_policy, render_terms
from pages.pricing import render_pricing
from pages.profile import render_profile
from pages.reports_page import render_reports
from pages.settings import render_settings
from pages.signup import render_signup_page
from pages.subscription import render_subscription
from pages.single_prediction import render_single_prediction
from pages.validation_results import render_validation_results
from services.qube_predict_client import health, refresh_account_state

APP_NAME = "QUBE Predict"
DEFAULT_API_URL = "http://localhost:8000"

PAGES: dict[str, Callable[[], None]] = {
    "Dashboard": render_dashboard,
    "Single Prediction": render_single_prediction,
    "Batch Prediction": render_batch_prediction,
    "Models": render_models,
    "Drug Library": render_drug_library,
    "Validation Reports": render_validation_results,
    "Model Diagnostics": render_model_diagnostics,
    "Usage": render_dashboard,
    "Billing": render_subscription,
    "Billing History": render_billing_history,
    "API Keys": render_profile,
    "Profile": render_profile,
    "Settings": render_settings,
    "About": render_about,
    "Privacy Policy": render_privacy_policy,
    "Terms": render_terms,
    "Refund Policy": render_refund_policy,
    "Contact": render_contact,
    "Admin": render_admin,
    "Pricing": render_pricing,
}

NAV_GROUPS: dict[str, list[str]] = {
    "Workspace": [
        "Dashboard",
        "Single Prediction",
        "Batch Prediction",
        "Models",
        "Drug Library",
        "Validation Reports",
        "Model Diagnostics",
    ],
    "Account": ["Usage", "Billing", "Pricing", "Billing History", "API Keys", "Profile"],
    "System": ["Settings", "About", "Privacy Policy", "Terms", "Refund Policy", "Contact", "Admin"],
}

PUBLIC_PAGES: dict[str, Callable[[], None]] = {
    "Login": lambda: render_login_page(_finish_auth),
    "Signup": render_signup_page,
    "About": render_about,
}


def initialize_application() -> None:
    st.session_state.setdefault("api_url", DEFAULT_API_URL)
    st.session_state.setdefault("access_token", "")
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("active_page", "Dashboard")
    st.session_state.setdefault("account", {})
    st.session_state.setdefault("api_key", "")
    st.session_state.setdefault("plan", "None")
    st.session_state.setdefault("subscription_status", "inactive")
    st.session_state.setdefault("monthly_limit", 0)
    st.session_state.setdefault("predictions_used", 0)
    st.session_state.setdefault("predictions_remaining", 0)
    st.session_state.setdefault("renewal_date", None)
    st.session_state.setdefault("avg_response_time", None)
    st.session_state.setdefault("backend_version", "Unknown")
    st.session_state.setdefault("reports", [])
    st.session_state.setdefault("show_admin", False)


def apply_theme() -> None:
    apply_enterprise_theme()


def _query_token() -> str:
    token = st.query_params.get("token", "")
    if isinstance(token, list):
        return token[0] if token else ""
    return token or ""


def _clear_auth() -> None:
    for key in ("access_token", "api_key"):
        st.session_state[key] = ""
    st.session_state.authenticated = False
    st.session_state.account = {}
    st.session_state.active_page = "Login"
    st.query_params.clear()


def _finish_auth(payload: dict) -> None:
    token = payload["access_token"]
    st.session_state.access_token = token
    st.query_params["token"] = token
    refresh_account_state()
    st.session_state.authenticated = True
    st.session_state.active_page = "Dashboard"
    st.rerun()


def _ensure_authenticated() -> bool:
    token = st.session_state.get("access_token") or _query_token()
    if not token:
        st.session_state.authenticated = False
        return False

    st.session_state.access_token = token
    try:
        refresh_account_state()
    except Exception:
        _clear_auth()
        return False

    st.session_state.authenticated = True
    return True


def render_public_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class="qube-sidebar-brand">
              <div class="qube-brand-mark">Q</div>
              <div>
                <div class="qube-brand-name">QUBE Predict</div>
                <div class="qube-brand-subtitle">Research Cloud</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="qube-sidebar-section">Authentication</div>', unsafe_allow_html=True)
        pages = list(PUBLIC_PAGES.keys())
        if st.session_state.active_page not in pages:
            st.session_state.active_page = "Login"
        page = st.session_state.active_page
        for public_page in pages:
            active = public_page == page
            label = f"{'● ' if active else ''}{public_page}"
            if st.button(label, key=f"public_nav_{public_page}", use_container_width=True, type="primary" if active else "secondary"):
                st.session_state.active_page = public_page
                st.rerun()
        return st.session_state.active_page


def render_sidebar() -> str:
    with st.sidebar:
        account = st.session_state.get("account", {})
        st.markdown(
            f"""
            <div class="qube-sidebar-brand">
              <div class="qube-brand-mark">Q</div>
              <div>
                <div class="qube-brand-name">QUBE Predict</div>
                <div class="qube-brand-subtitle">{esc(account.get("email", "Research workspace"))}</div>
              </div>
            </div>
            {status_pill("Logged In", "blue")}
            """,
            unsafe_allow_html=True,
        )

        pages = [page for items in NAV_GROUPS.values() for page in items]
        if st.session_state.active_page not in pages:
            st.session_state.active_page = "Dashboard"

        page = st.session_state.active_page
        for group, group_pages in NAV_GROUPS.items():
            st.markdown(f'<div class="qube-sidebar-section">{esc(group)}</div>', unsafe_allow_html=True)
            for group_page in group_pages:
                active = group_page == page
                label = f"{'● ' if active else ''}{group_page}"
                if st.button(label, key=f"nav_{group}_{group_page}", use_container_width=True, type="primary" if active else "secondary"):
                    page = group_page
                    st.session_state.active_page = group_page
                    st.rerun()

        st.session_state.active_page = page
        st.divider()

        try:
            payload = health()
        except Exception:
            payload = {"status": "offline"}
        cloud_status = "Connected" if payload.get("status") == "online" else "Offline"
        st.session_state.backend_version = payload.get("version", st.session_state.get("backend_version", "Unknown"))
        current_model = st.session_state.get("single_drug") or st.session_state.get("batch_drug") or "Auto-select"
        st.markdown(
            f"""
            <div class="qube-sidebar-section">Cloud Status</div>
            <div class="qube-status-grid">
              <div class="qube-status-row"><span>Cloud Status</span><span class="qube-status-value">{esc(cloud_status)}</span></div>
              <div class="qube-status-row"><span>Backend Status</span><span class="qube-status-value">{esc(payload.get("status", "unknown"))}</span></div>
              <div class="qube-status-row"><span>API Version</span><span class="qube-status-value">{esc(payload.get("version", "Unknown"))}</span></div>
              <div class="qube-status-row"><span>Current Model</span><span class="qube-status-value">{esc(current_model)}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        if st.button("Logout", use_container_width=True):
            _clear_auth()
            st.rerun()
        return page


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="Q", layout="wide", initial_sidebar_state="expanded")
    initialize_application()
    apply_theme()

    if not _ensure_authenticated():
        page = render_public_sidebar()
        PUBLIC_PAGES[page]()
        return

    page = render_sidebar()
    try:
        PAGES[page]()
        footer()
    except Exception as exc:
        st.error("Application Error")
        with st.expander("Technical Details"):
            st.exception(exc)


if __name__ == "__main__":
    main()





