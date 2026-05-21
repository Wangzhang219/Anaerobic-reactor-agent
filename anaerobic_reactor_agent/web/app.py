"""厌氧反应器智能诊断系统 — Web 入口."""

import streamlit as st

st.set_page_config(
    page_title="厌氧反应器智能诊断系统",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

from anaerobic_reactor_agent.web.session_state import init_session_state
from anaerobic_reactor_agent.web.views.dashboard import render_dashboard
from anaerobic_reactor_agent.web.components.sidebar import render_sidebar


def main():
    init_session_state()
    render_sidebar()

    st.title("🧪 厌氧反应器智能诊断系统")
    st.caption("参数监测 · 故障诊断 · 操作建议 · AI 专家分析")
    render_dashboard()


if __name__ == "__main__":
    main()
