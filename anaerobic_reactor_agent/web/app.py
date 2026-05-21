"""Streamlit web application entry point."""

import streamlit as st

st.set_page_config(
    page_title="厌氧反应器智能诊断系统",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

from anaerobic_reactor_agent.web.session_state import init_session_state
from anaerobic_reactor_agent.web.pages.dashboard import render_dashboard
from anaerobic_reactor_agent.web.pages.history import render_history
from anaerobic_reactor_agent.web.components.sidebar import render_sidebar


def main():
    init_session_state()
    render_sidebar()

    st.title("厌氧反应器智能诊断系统")
    st.caption("实时监测 · 故障诊断 · 操作建议")

    tab1, tab2 = st.tabs(["诊断面板", "历史趋势"])

    with tab1:
        render_dashboard()

    with tab2:
        render_history()


if __name__ == "__main__":
    main()
