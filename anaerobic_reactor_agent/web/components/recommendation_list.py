"""Prioritized recommendation list with urgency levels."""

import streamlit as st
from anaerobic_reactor_agent.models.diagnosis import DiagnosisResult

LEVEL_COLORS = {"immediate": "#ef4444", "long_term": "#f59e0b", "preventive": "#3b82f6"}
LEVEL_NAMES = {"immediate": "紧急处理", "long_term": "长期措施", "preventive": "预防建议"}


def render_recommendation_list(result: DiagnosisResult):
    """Render a numbered list of graded recommendations."""

    if not result.recommendations:
        return

    st.subheader(f"操作建议（共 {len(result.recommendations)} 条）")

    for i, rec in enumerate(result.recommendations, 1):
        color = LEVEL_COLORS.get(rec.level, "#888")
        level_name = LEVEL_NAMES.get(rec.level, rec.level)
        st.markdown(
            f"{i}. <span style='color:{color};font-weight:bold'>[{level_name}]</span> {rec.text}",
            unsafe_allow_html=True,
        )
