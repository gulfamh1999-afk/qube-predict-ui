"""Shared page navigation for the Streamlit application."""

from __future__ import annotations

import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from ui.theme import PAGE_KEY


try:
    cookies = EncryptedCookieManager(
        prefix="qube_predict/",
        password="QUBE_PREDICT_CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_2026",
    )
except Exception:
    cookies = None


def cookies_ready() -> bool:
    """Return whether browser cookie storage is currently available."""

    try:
        return cookies is not None and bool(cookies.ready())
    except Exception:
        return False


def read_cookie(name: str):
    """Read a cookie without allowing storage failures to interrupt the app."""

    if not cookies_ready():
        return None
    try:
        return cookies.get(name)
    except Exception:
        return None


def write_cookies(values: dict[str, str | None]) -> None:
    """Persist cookies when available; storage errors are non-fatal."""

    if not cookies_ready():
        return
    try:
        for name, value in values.items():
            if value is not None:
                cookies[name] = value
        cookies.save()
    except Exception:
        return


def navigate_to(page: str) -> None:
    """Set the active page and persist it for the next browser session."""

    st.session_state[PAGE_KEY] = page
    write_cookies({"page": page})