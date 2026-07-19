"""Streamlit entry point for QUBE Predict UI.

This app shell is intentionally wired to this project's existing structure:
- backend/ for API client and session defaults
- ui/ for project theme assets
- views/ for page renderers

Do not import pages that are not present in views/.
"""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from backend.api_client import ApiClient
from backend.state import initialize_state
from components.qube_ui import apply_enterprise_theme, esc, footer, status_pill
from ui.theme import APP_NAME, APP_SUBTITLE, ENGINE_VERSION, PAGE_KEY, apply_theme as apply_project_theme
from views.about import render_about
from views.api_keys import render_api_keys
from views.batch_prediction import render_batch_prediction
from views.billing import render_billing
from views.billing_history import render_billing_history
from views.contact import render_contact
from views.dashboard import render_dashboard
from views.login import render_login
from views.logout import render_logout
from views.privacy_policy import render_privacy_policy
from views.profile import render_profile
from views.refund_policy import render_refund_policy
from views.signup import render_signup
from views.single_prediction import render_single_prediction
from views.terms import render_terms
from views.usage import render_usage

DEFAULT_API_URL = "http://127.0.0.1:8000"

PageRenderer = Callable[[ApiClient], None]

PUBLIC_PAGES: dict[str, PageRenderer] = {
    "Login": render_login,
    "Signup": render_signup,
    "About": render_about,
    "Contact": render_contact,
    "Privacy Policy": render_privacy_policy,
    "Terms": render_terms,
    "Refund Policy": render_refund_policy,
}

PROTECTED_PAGES: dict[str, PageRenderer] = {
    "Dashboard": render_dashboard,
    "Single Prediction": render_single_prediction,
    "Batch Prediction": render_batch_prediction,
    "Usage": render_usage,
    "Billing": render_billing,
    "Billing History": render_billing_history,
    "API Keys": render_api_keys,
    "Profile": render_profile,
    "About": render_about,
    "Contact": render_contact,
    "Privacy Policy": render_privacy_policy,
    "Terms": render_terms,
    "Refund Policy": render_refund_policy,
    "Logout": render_logout,
}

NAV_GROUPS: dict[str, list[str]] = {
    "Workspace": ["Dashboard", "Single Prediction", "Batch Prediction"],
    "Account": ["Usage", "Billing", "Billing History", "API Keys", "Profile"],
    "System": ["About", "Contact", "Privacy Policy", "Terms", "Refund Policy", "Logout"],
}


def initialize_application() -> None:
    initialize_state()
    st.session_state.setdefault("api_url", DEFAULT_API_URL)
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("jwt", None)
    st.session_state.setdefault("refresh_token", None)
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("api_key", None)
    st.session_state.setdefault(PAGE_KEY, "Dashboard")


def apply_shell_theme() -> None:
    apply_project_theme()
    apply_enterprise_theme()


def _current_user_label() -> str:
    user = st.session_state.get("user")
    if isinstance(user, dict):
        return user.get("email") or user.get("full_name") or "Research workspace"
    return "Research workspace"


def _render_brand(subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="qube-sidebar-brand">
          <div class="qube-brand-mark">Q</div>
          <div>
            <div class="qube-brand-name">{esc(APP_NAME)}</div>
            <div class="qube-brand-subtitle">{esc(subtitle)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _set_page(page: str) -> None:
    st.session_state[PAGE_KEY] = page


def render_public_sidebar() -> str:
    pages = list(PUBLIC_PAGES)
    if st.session_state.get(PAGE_KEY) not in pages:
        _set_page("Login")

    with st.sidebar:
        _render_brand("Research Cloud")
        st.markdown('<div class="qube-sidebar-section">Authentication</div>', unsafe_allow_html=True)

        current_page = st.session_state[PAGE_KEY]
        for page in pages:
            active = page == current_page
            if st.button(
                page,
                key=f"public_nav_{page}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                _set_page(page)
                st.rerun()

        st.divider()
        st.markdown(
            f"""
            <div class="qube-status-grid">
              <div class="qube-status-row"><span>Frontend</span><span class="qube-status-value">Streamlit</span></div>
              <div class="qube-status-row"><span>Engine</span><span class="qube-status-value">{esc(ENGINE_VERSION)}</span></div>
              <div class="qube-status-row"><span>Backend</span><span class="qube-status-value">{esc(st.session_state.get('api_url', DEFAULT_API_URL))}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state[PAGE_KEY]


def render_authenticated_sidebar() -> str:
    pages = list(PROTECTED_PAGES)
    if st.session_state.get(PAGE_KEY) not in pages:
        _set_page("Dashboard")

    with st.sidebar:
        _render_brand(_current_user_label())
        st.markdown(status_pill("Logged In", "blue"), unsafe_allow_html=True)

        current_page = st.session_state[PAGE_KEY]
        for group, group_pages in NAV_GROUPS.items():
            available_pages = [page for page in group_pages if page in PROTECTED_PAGES]
            if not available_pages:
                continue

            st.markdown(f'<div class="qube-sidebar-section">{esc(group)}</div>', unsafe_allow_html=True)
            for page in available_pages:
                active = page == current_page
                if st.button(
                    page,
                    key=f"nav_{group}_{page}",
                    use_container_width=True,
                    type="primary" if active else "secondary",
                ):
                    _set_page(page)
                    st.rerun()

        st.divider()
        st.markdown(
            f"""
            <div class="qube-sidebar-section">Cloud Status</div>
            <div class="qube-status-grid">
              <div class="qube-status-row"><span>Cloud Status</span><span class="qube-status-value">Connected</span></div>
              <div class="qube-status-row"><span>Auth</span><span class="qube-status-value">JWT</span></div>
              <div class="qube-status-row"><span>Engine</span><span class="qube-status-value">{esc(ENGINE_VERSION)}</span></div>
              <div class="qube-status-row"><span>Backend</span><span class="qube-status-value">{esc(st.session_state.get('api_url', DEFAULT_API_URL))}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state[PAGE_KEY]


def main() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="Q",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    initialize_application()
    apply_shell_theme()

    client = ApiClient()

    if st.session_state.get("authenticated", False):
        page = render_authenticated_sidebar()
        renderer = PROTECTED_PAGES.get(page, render_dashboard)
    else:
        page = render_public_sidebar()
        renderer = PUBLIC_PAGES.get(page, render_login)

    try:
        renderer(client)
        footer()
    except Exception as exc:
        st.error("Application Error")
        with st.expander("Technical Details"):
            st.exception(exc)


if __name__ == "__main__":
    main()
