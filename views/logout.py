from __future__ import annotations

import streamlit as st


def _request_browser_storage_sync(action: str = "clear") -> None:
    st.session_state["_browser_storage_action"] = action
    st.session_state["_browser_storage_nonce"] = st.session_state.get("_browser_storage_nonce", 0) + 1


def render_logout(client):

    st.title("🚪 Logout")

    if not st.session_state.get("authenticated", False):

        st.info("You are already logged out.")

        if st.button(
            "Go to Login",
            use_container_width=True,
        ):
            st.session_state.page = "Login"
            _request_browser_storage_sync("clear")
            st.rerun()

        return

    st.warning(
        "Are you sure you want to log out of QUBE Predict?"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🚪 Logout",
            type="primary",
            use_container_width=True,
        ):

            try:
                client.logout()
            except Exception:
                pass

            # Clear session
            st.session_state.authenticated = False
            st.session_state.jwt = None
            st.session_state.refresh_token = None
            st.session_state.user = None
            st.session_state.api_key = None
            st.session_state.page = "Login"

            _request_browser_storage_sync("clear")

            st.success("You have been logged out successfully.")

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.page = "Dashboard"
            _request_browser_storage_sync("save")
            st.rerun()
