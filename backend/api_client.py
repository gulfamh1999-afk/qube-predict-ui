from __future__ import annotations

import requests
import streamlit as st


class ApiClient:

    def __init__(self):

        self.base_url = st.session_state.get("api_url")

        if not self.base_url:
            try:
                self.base_url = st.secrets.get(
                    "API_URL",
                    "https://qube-predict-api.onrender.com",
                )
            except Exception:
                self.base_url = "https://qube-predict-api.onrender.com"

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

        # ------------------------------------------------------
        # Public endpoints must NOT receive stale credentials
        # ------------------------------------------------------

        public_endpoints = {
            "/login",
            "/signup",
            "/forgot-password",
            "/reset-password",
        }

        if endpoint not in public_endpoints:
            headers.update(self._headers())

        try:

            response = requests.request(
                method,
                url,
                headers=headers,
                timeout=120,
                **kwargs,
            )

        except requests.RequestException as e:

            raise Exception(
                f"Could not connect to QUBE Predict API: {e}"
            )

        # ------------------------------------------------------
        # Authentication
        # ------------------------------------------------------

        if response.status_code == 401:

            if endpoint == "/login":

                try:
                    detail = response.json().get(
                        "detail",
                        "Incorrect email or password",
                    )
                except Exception:
                    detail = "Incorrect email or password"

                raise Exception(detail)

            st.session_state.authenticated = False
            st.session_state.jwt = None
            st.session_state.refresh_token = None
            st.session_state.user = None

            raise Exception("Authentication expired.")

        # ------------------------------------------------------
        # Other API errors
        # ------------------------------------------------------

        if not response.ok:

            try:
                data = response.json()
                detail = data.get("detail", response.text)
            except Exception:
                detail = response.text

            raise Exception(
                f"API error {response.status_code}: {detail}"
            )

        # ------------------------------------------------------
        # Response
        # ------------------------------------------------------

        if response.content:

            try:
                return response.json()
            except ValueError:

                raise Exception(
                    "API returned an invalid JSON response."
                )

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

        refresh_token = st.session_state.get(
            "refresh_token"
        )

        if not refresh_token:
            raise Exception("No refresh token available.")

        result = self._request(
            "POST",
            "/refresh",
            json={
                "refresh_token": refresh_token
            },
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