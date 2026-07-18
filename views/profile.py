from __future__ import annotations

import streamlit as st


def render_profile(client):
    st.title("👤 Profile")

    if not st.session_state.get("authenticated", False):
        st.warning("Please login first.")
        return

    # -------------------------------
    # Load profile from backend
    # -------------------------------
    try:
        user = client.me()
        st.session_state.user = user
    except Exception as e:
        st.error(f"Unable to load profile.\n\n{e}")
        return

    st.subheader("Personal Information")

    with st.form("profile_form"):
        st.text_input(
            "Email",
            value=user.get("email", ""),
            disabled=True,
        )

        full_name = st.text_input(
            "Full Name",
            value=user.get("full_name", ""),
        )

        company = st.text_input(
            "Company",
            value=user.get("company", ""),
        )

        country = st.text_input(
            "Country",
            value=user.get("country", ""),
        )

        save = st.form_submit_button(
            "💾 Save Changes",
            use_container_width=True,
        )

    if save:
        payload = {
            "full_name": full_name,
            "company": company,
            "country": country,
        }

        try:
            updated = client.update_profile(payload)
            st.session_state.user = updated
            st.success("Profile updated successfully.")
            st.rerun()

        except Exception as e:
            st.error(f"Profile update failed.\n\n{e}")

    st.divider()

    st.subheader("Account")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Account Status",
            "Active" if user.get("is_active", False) else "Inactive",
        )

    with col2:
        st.metric(
            "Email Verified",
            "Yes" if user.get("email_verified", False) else "No",
        )

    st.divider()

    st.subheader("Developer Information")

    st.code(
        f"""User ID        : {user.get('id', '-')}

Email          : {user.get('email', '-')}

Created At     : {user.get('created_at', '-')}

Last Login     : {user.get('last_login', '-')}
""",
        language="text",
    )

    api_key = st.session_state.get("api_key")

    if api_key:
        st.divider()

        st.subheader("API Access")

        st.text_input(
            "API Key",
            value=api_key,
            disabled=True,
        )

        st.caption(
            "Use this API key to access the QUBE Predict REST API."
        )