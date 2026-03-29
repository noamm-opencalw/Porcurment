"""Streamlit session state helpers for Porcurment."""

import streamlit as st


def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "search_query": "",
        "search_running": False,
        "search_stage": "",
        "results": None,
        "all_deals": None,
        "search_history": [],
        "selected_history": None,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def set_results(results: dict | None):
    """Store search results in session state."""
    st.session_state.results = results
    st.session_state.search_running = False
    st.session_state.search_stage = ""


def add_to_history(query: str, results: dict | None):
    """Add a search to history."""
    st.session_state.search_history.insert(
        0,
        {
            "query": query,
            "results": results,
            "deals_count": len(results.get("deals", [])) if results else 0,
        },
    )
    # Keep last 20 searches
    st.session_state.search_history = st.session_state.search_history[:20]
