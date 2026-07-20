from __future__ import annotations

import requests
import streamlit as st


class ApiClient:

    def __init__(self):

        self.base_url = st.session_state.get("api_url")

        if not self.base_url:
            self.base_url = st.secrets.get(
                "API_URL",
                "https://qube-predict.onrender.com"
            )

        self.base_url = self.base_url.rstrip("/")

    # ==========================================================
    # INTERNAL
    # ==========================================================

    def _headers(self):

        headers = {}

        jwt = st.session_state.get("jwt")

        if jwt:
            headers["Authorization"] = f"Bearer {jwt}"

        api_key = st.session_state.get("api_key")

        if api_key:
            headers["x-api-key"] = api_key

        return headers

    def _request(
        self,
        method,
        endpoint,
        **kwargs,
    ):

        url = f"{self.base_url}{endpoint}"

        headers = kwargs.pop("headers", {})

        headers.update(self._headers())

        response = requests.request(
            method,
            url,
            headers=headers,
            timeout=60,
            **kwargs,
        )

        if response.status_code == 401:

            st.session_state.authenticated = False

            st.session_state.jwt = None

            st.session_state.refresh_token = None

            st.session_state.user = None

            raise Exception("Authentication expired.")

        response.raise_for_status()

        if response.content:

            return response.json()

        return {}

    # ==========================================================
    # AUTH
    # ==========================================================

    def signup(
        self,
        data,
    ):

        return self._request(
            "POST",
            "/signup",
            json=data,
        )

    def login(
        self,
        email,
        password,
        remember=False,
    ):

        payload = {
            "email": email,
            "password": password,
            "remember_me": remember,
        }

        result = self._request(
            "POST",
            "/login",
            json=payload,
        )

        st.session_state.jwt = result["access_token"]

        st.session_state.refresh_token = result["refresh_token"]

        st.session_state.authenticated = True

        return result

    def refresh(self):

        payload = {
            "refresh_token":
            st.session_state.refresh_token
        }

        result = self._request(
            "POST",
            "/refresh",
            json=payload,
        )

        st.session_state.jwt = result["access_token"]

        st.session_state.refresh_token = result["refresh_token"]

        return result

    def forgot_password(
        self,
        email,
    ):

        return self._request(
            "POST",
            "/forgot-password",
            json={
                "email": email
            },
        )

    def reset_password(
        self,
        token,
        password,
        confirm,
    ):

        return self._request(
            "POST",
            "/reset-password",
            json={
                "token": token,
                "new_password": password,
                "new_password_confirm": confirm,
            },
        )

    # ==========================================================
    # USER
    # ==========================================================

    def me(self):

        return self._request(
            "GET",
            "/me",
        )

    def update_profile(
        self,
        profile,
    ):

        return self._request(
            "PUT",
            "/me",
            json=profile,
        )

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    def dashboard(self):

        return self._request(
            "GET",
            "/dashboard",
        )

    # ==========================================================
    # BILLING
    # ==========================================================

    def plans(self):

        return self._request(
            "GET",
            "/billing/plans",
        )

    def create_subscription(
        self,
        plan,
    ):

        return self._request(
            "POST",
            "/billing/create-subscription",
            params={
                "plan": plan
            },
        )

    def subscription(self):

        return self._request(
            "GET",
            "/billing/subscription",
        )

    def billing_history(self):

        return self._request(
            "GET",
            "/billing/history",
        )

    def cancel_subscription(self):

        return self._request(
            "POST",
            "/billing/cancel",
        )

    # ==========================================================
    # PREDICTION
    # ==========================================================

    def predict(
        self,
        drug,
        sample,
    ):

        return self._request(
            "POST",
            "/api/v1/predict",
            json={
                "drug": drug,
                "sample": sample,
            },
        )

    def batch_predict(
        self,
        drug,
        files,
    ):

        return self._request(
            "POST",
            "/api/v1/predict/batch",
            params={
                "drug_name": drug
            },
            files=files,
        )

    # ==========================================================
    # MODELS
    # ==========================================================

    def models(self):

        return self._request(
            "GET",
            "/api/v1/models",
        )

    # ==========================================================
    # LOGOUT
    # ==========================================================

    def logout(self):

        st.session_state.authenticated = False

        st.session_state.jwt = None

        st.session_state.refresh_token = None

        st.session_state.user = None

        st.session_state.api_key = None

        return True