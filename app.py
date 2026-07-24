"""Streamlit entry point for QUBE Predict UI.

This app shell is intentionally wired to this project's existing structure:
- backend/ for API client and session defaults
- ui/ for project theme assets
- views/ for page renderers

Do not import pages that are not present in views/.
"""

from __future__ import annotations

from collections.abc import Callable
import json
import os

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

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

def _default_api_url() -> str:
    try:
        return st.secrets.get("API_URL", os.getenv("API_URL", "https://qube-predict.onrender.com"))
    except Exception:
        return os.getenv("API_URL", "https://qube-predict.onrender.com")


DEFAULT_API_URL = _default_api_url()

STORAGE_JWT_KEY = "qube_predict.jwt"
STORAGE_REFRESH_KEY = "qube_predict.refresh_token"
STORAGE_PAGE_KEY = "qube_predict.page"
STORAGE_RESTORE_FLAG = "_browser_storage_restored"
STORAGE_ACTION_KEY = "_browser_storage_action"
STORAGE_NONCE_KEY = "_browser_storage_nonce"


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

VALID_PAGES = set(PUBLIC_PAGES) | set(PROTECTED_PAGES)


def _browser_storage_eval(js_expression: str, key: str):
    return streamlit_js_eval(
        js_expressions=js_expression,
        key=key,
        want_output=True,
    )


def _restore_browser_storage_script() -> str:
    return f"""
(() => JSON.stringify({{
  jwt: window.localStorage.getItem({json.dumps(STORAGE_JWT_KEY)}),
  refresh_token: window.localStorage.getItem({json.dumps(STORAGE_REFRESH_KEY)}),
  page: window.localStorage.getItem({json.dumps(STORAGE_PAGE_KEY)})
}}))()
"""


def _save_browser_storage_script() -> str:
    jwt = st.session_state.get("jwt")
    refresh_token = st.session_state.get("refresh_token")
    page = st.session_state.get(PAGE_KEY)

    return f"""
(() => {{
  const jwtKey = {json.dumps(STORAGE_JWT_KEY)};
  const refreshKey = {json.dumps(STORAGE_REFRESH_KEY)};
  const pageKey = {json.dumps(STORAGE_PAGE_KEY)};
  const jwt = {json.dumps(jwt)};
  const refreshToken = {json.dumps(refresh_token)};
  const page = {json.dumps(page)};

  if (jwt) {{
    window.localStorage.setItem(jwtKey, jwt);
  }} else {{
    window.localStorage.removeItem(jwtKey);
  }}

  if (refreshToken) {{
    window.localStorage.setItem(refreshKey, refreshToken);
  }} else {{
    window.localStorage.removeItem(refreshKey);
  }}

  if (page) {{
    window.localStorage.setItem(pageKey, page);
  }} else {{
    window.localStorage.removeItem(pageKey);
  }}

  return "ok";
}})()
"""


def _clear_browser_storage_script() -> str:
    return f"""
(() => {{
  window.localStorage.removeItem({json.dumps(STORAGE_JWT_KEY)});
  window.localStorage.removeItem({json.dumps(STORAGE_REFRESH_KEY)});
  window.localStorage.removeItem({json.dumps(STORAGE_PAGE_KEY)});
  return "ok";
}})()
"""


def _request_browser_storage_sync(action: str = "save") -> None:
    st.session_state[STORAGE_ACTION_KEY] = action
    st.session_state[STORAGE_NONCE_KEY] = st.session_state.get(STORAGE_NONCE_KEY, 0) + 1


def _restore_browser_storage() -> None:
    if st.session_state.get(STORAGE_RESTORE_FLAG):
        return

    payload = _browser_storage_eval(
        _restore_browser_storage_script(),
        key="qube_predict_restore_storage",
    )

    if payload is None:
        st.stop()

    st.session_state[STORAGE_RESTORE_FLAG] = True

    try:
        restored = json.loads(payload) if payload else {}
    except json.JSONDecodeError:
        restored = {}

    saved_page = restored.get("page")
    if saved_page in VALID_PAGES:
        st.session_state[PAGE_KEY] = saved_page

    if not st.session_state.get("authenticated"):
        jwt = restored.get("jwt")
        refresh_token = restored.get("refresh_token")

        if jwt:
            st.session_state.jwt = jwt

        if refresh_token:
            st.session_state.refresh_token = refresh_token


def _sync_browser_storage() -> None:
    action = st.session_state.get(STORAGE_ACTION_KEY)
    if not action:
        return

    nonce = st.session_state.get(STORAGE_NONCE_KEY, 0)
    script = _clear_browser_storage_script() if action == "clear" else _save_browser_storage_script()
    result = _browser_storage_eval(
        script,
        key=f"qube_predict_sync_storage_{action}_{nonce}",
    )

    if result is None:
        st.stop()

    st.session_state[STORAGE_ACTION_KEY] = None


def initialize_application() -> None:

    initialize_state()

    st.session_state.setdefault("api_url", DEFAULT_API_URL)
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("jwt", None)
    st.session_state.setdefault("refresh_token", None)
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("api_key", None)
    st.session_state.setdefault(PAGE_KEY, "Dashboard")

    _restore_browser_storage()
    _sync_browser_storage()


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
    _request_browser_storage_sync("save")


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


def _restore_authenticated_session(client: ApiClient) -> None:
    if not st.session_state.get("refresh_token"):
        return

    if st.session_state.get("authenticated"):
        return

    try:
        client.refresh()
        user = client.me()

        st.session_state.authenticated = True
        st.session_state.user = user

        if isinstance(user, dict):
            st.session_state.api_key = user.get("api_key")

        _request_browser_storage_sync("save")
        st.rerun()

    except Exception:
        st.session_state.authenticated = False
        st.session_state.jwt = None
        st.session_state.refresh_token = None
        st.session_state.user = None
        st.session_state.api_key = None
        st.session_state[PAGE_KEY] = "Login"
        _request_browser_storage_sync("clear")
        st.rerun()


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

    _restore_authenticated_session(client)

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
