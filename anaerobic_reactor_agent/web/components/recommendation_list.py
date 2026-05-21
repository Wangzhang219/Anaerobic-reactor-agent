"""Compact recommendation list."""

import streamlit as st
from anaerobic_reactor_agent.models.diagnosis import DiagnosisResult

LEVEL_COLORS = {"immediate": "#ef4444", "long_term": "#f59e0b", "preventive": "#3b82f6"}
LEVEL_BADGES = {"immediate": "紧急", "long_term": "长期", "preventive": "预防"}


def render_recommendation_list(result: DiagnosisResult):
    """紧凑型分级建议列表。"""

    if not result.recommendations:
        return

    for i, rec in enumerate(result.recommendations, 1):
        color = LEVEL_COLORS.get(rec.level, "#888")
        badge = LEVEL_BADGES.get(rec.level, rec.level)
        st.markdown(
            f"{i}. <span style='color:{color};font-weight:bold'>[{badge}]</span> {rec.text}",
            unsafe_allow_html=True,
        )
