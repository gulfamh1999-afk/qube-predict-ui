from __future__ import annotations

import streamlit as st


def render_signup(client):

    st.title("📝 Create Account")

    st.caption("Create your QUBE Predict account")

    # Already logged in
    if st.session_state.get("authenticated", False):
        st.success("You are already signed in.")
        if st.button("Go to Dashboard", use_container_width=True):
            st.rerun()
        return

    with st.form("signup_form", clear_on_submit=False):

        full_name = st.text_input(
            "Full Name",
            placeholder="John Doe",
        )

        company = st.text_input(
            "Company",
            placeholder="Acme Bio",
        )

        country = st.text_input(
            "Country",
            placeholder="India",
        )

        email = st.text_input(
            "Email",
            placeholder="name@example.com",
        )

        password = st.text_input(
            "Password",
            type="password",
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True,
        )

    if submitted:

        if not full_name:
            st.error("Please enter your name.")
            return

        if not email:
            st.error("Please enter your email.")
            return

        if len(password) < 8:
            st.error("Password must be at least 8 characters.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        payload = {
            "email": email,
            "password": password,
            "password_confirm": confirm_password,
            "full_name": full_name,
            "company": company,
            "country": country,
        }

        with st.spinner("Creating account..."):

            try:

                client.signup(payload)

                st.success("✅ Account created successfully!")

                st.info("Please log in using your new account.")

                if st.button(
                    "Go to Login",
                    use_container_width=True,
                    key="goto_login_after_signup",
                ):
                    st.rerun()

            except Exception as e:

                st.error(str(e))

    st.divider()

    if st.button(
        "Already have an account? Login",
        use_container_width=True,
    ):
        st.session_state.page = "Login"
        st.rerun()