"""Shared page navigation for the Streamlit application."""

from __future__ import annotations

import streamlit as st

from ui.theme import PAGE_KEY


def cookies_ready() -> bool:
    """Browser cookie storage is unavailable in this compatibility version."""
    return False


def read_cookie(name: str):
    """Return no cookie; session state is used for navigation."""
    return None


def write_cookies(values: dict[str, str | None]) -> None:
    """Cookie persistence disabled; session state remains the source of truth."""
    return


def navigate_to(page: str) -> None:
    """Set the active page for the current Streamlit session."""
    st.session_state[PAGE_KEY] = page