from __future__ import annotations

import streamlit as st


def render_logout(client):
    st.title("🚪 Logout")

    if not st.session_state.get("authenticated", False):
        st.info("You are already logged out.")

        if st.button(
            "Go to Login",
            use_container_width=True,
        ):
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

            # Remove authentication data
            for key in [
                "authenticated",
                "jwt",
                "refresh_token",
                "api_key",
                "user",
            ]:
                st.session_state.pop(key, None)

            st.success("You have been logged out successfully.")

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):
            st.rerun()