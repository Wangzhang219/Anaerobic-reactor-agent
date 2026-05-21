"""Streamlit session state initialization."""

import streamlit as st


def init_session_state():
    """Initialize all session state keys on first page load."""
    defaults = {
        "reactor_params": None,
        "diagnosis_result": None,
        "llm_provider": None,
        "history": [],
        "api_key_configured": False,
        "llm_enabled": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
