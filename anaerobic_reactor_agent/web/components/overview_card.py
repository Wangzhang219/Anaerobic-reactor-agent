"""Overall reactor status overview card with radar chart."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from anaerobic_reactor_agent.models.diagnosis import DiagnosisResult, ParameterStatus

PARAMETER_NAMES_CN = {
    "ph": "pH值", "temperature": "温度", "vfa": "VFA",
    "alkalinity": "碱度", "orp": "ORP", "biogas_production": "产气量",
    "methane_content": "甲烷含量", "olr": "有机负荷", "hrt": "HRT",
    "nh3_n": "氨氮", "cod_removal_rate": "COD去除率",
    "vfa_alkalinity_ratio": "VFA/碱度比",
}


def render_overview_card(result: DiagnosisResult):
    """Render the overall status overview card with key metrics and radar chart."""

    col1, col2, col3, col4 = st.columns(4)

    status = result.overall_status
    if status == ParameterStatus.NORMAL:
        label, color = "正常运行", "#10b981"
    elif status == ParameterStatus.WARNING:
        label, color = "注意预警", "#f59e0b"
    else:
        label, color = "异常报警", "#ef4444"

    with col1:
        st.metric(label="反应器状态", value=label)
        emoji = "🟢" if status == ParameterStatus.NORMAL else "🟡" if status == ParameterStatus.WARNING else "🔴"
        st.markdown(f"<h1 style='color:{color}; margin:0;'>{emoji}</h1>", unsafe_allow_html=True)

    with col2:
        cod_assess = _find_assessment(result, "cod_removal_rate")
        if cod_assess:
            st.metric(label="COD 去除率", value=f"{cod_assess.current_value}%")

    with col3:
        ratio_assess = _find_assessment(result, "vfa_alkalinity_ratio")
        if ratio_assess:
            st.metric(label="VFA / 碱度 比值", value=f"{ratio_assess.current_value}")

    with col4:
        st.metric(label="检测到故障数", value=str(result.fault_count))

    # Radar chart for parameter health
    st.divider()
    st.subheader("参数健康度雷达图")

    radar_data = []
    for a in result.parameter_assessments:
        cn = PARAMETER_NAMES_CN.get(a.parameter_name, a.parameter_name)
        if a.parameter_name in ("cod_inlet", "cod_outlet", "nh3_n", "reactor_type"):
            continue  # skip raw inputs, show only indicators
        radar_data.append((cn, a.health_score * 100))

    if radar_data:
        labels = [r[0] for r in radar_data]
        values = [r[1] for r in radar_data]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            fillcolor='rgba(16, 185, 129, 0.25)',
            line=dict(color='#10b981', width=2),
            name='健康度 (%)',
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(range=[0, 100], ticksuffix="%"),
            ),
            height=350,
            margin=dict(l=40, r=40, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()


def _find_assessment(result: DiagnosisResult, param_name: str):
    for a in result.parameter_assessments:
        if a.parameter_name == param_name:
            return a
    return None
