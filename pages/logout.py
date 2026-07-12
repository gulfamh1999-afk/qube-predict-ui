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
            st.session_state.page = "Login"
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

                # Call client logout (clears session)
                client.logout()

            except Exception:
                # Continue with local cleanup even if client logout fails
                pass

            # Clear Streamlit session
            keys_to_clear = [
                "authenticated",
                "jwt",
                "refresh_token",
                "api_key",
                "user",
            ]

            for key in keys_to_clear:
                st.session_state[key] = None

            st.session_state.authenticated = False
            st.session_state.page = "Login"

            st.success("You have been logged out successfully.")

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):
            st.session_state.page = "Dashboard"
            st.rerun()