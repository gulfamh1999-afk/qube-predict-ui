from __future__ import annotations

import streamlit as st


def render_login(client):

    st.title("🔐 Login")

    st.caption("Sign in to your QUBE Predict account")

    # Already logged in
    if st.session_state.get("authenticated", False):
        st.success("You are already logged in.")
        if st.button("Go to Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()
        return

    with st.form("login_form", clear_on_submit=False):

        email = st.text_input(
            "Email",
            placeholder="name@example.com",
        )

        password = st.text_input(
            "Password",
            type="password",
        )

        remember = st.checkbox(
            "Remember me",
            value=False,
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

    if submitted:

        if not email or not password:
            st.error("Please enter your email and password.")
            return

        with st.spinner("Signing in..."):

            try:

                token = client.login(
                    email=email,
                    password=password,
                    remember=remember,
                )

                # Load profile
                user = client.me()

                st.session_state.authenticated = True
                st.session_state.jwt = token["access_token"]
                st.session_state.refresh_token = token["refresh_token"]
                st.session_state.user = user

                # Try loading API key if backend returns it
                if isinstance(user, dict):
                    st.session_state.api_key = user.get("api_key")

                st.success("Login successful!")

                st.session_state.page = "Dashboard"

                st.rerun()

            except Exception as e:

                st.error(str(e))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Create Account",
            use_container_width=True,
        ):
            st.session_state.page = "Signup"
            st.rerun()

    with col2:
        if st.button(
            "Forgot Password",
            use_container_width=True,
        ):
            st.info(
                "Password reset is available through the backend API."
            )