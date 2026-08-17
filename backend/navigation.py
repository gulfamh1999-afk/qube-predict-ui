"""Shared page navigation for the Streamlit application."""

from __future__ import annotations

import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from ui.theme import PAGE_KEY


cookies = EncryptedCookieManager(
    prefix="qube_predict/",
    password="QUBE_PREDICT_CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_2026",
)


def navigate_to(page: str) -> None:
    """Set the active page and persist it for the next browser session."""

    st.session_state[PAGE_KEY] = page
    cookies["page"] = page
    cookies.save()