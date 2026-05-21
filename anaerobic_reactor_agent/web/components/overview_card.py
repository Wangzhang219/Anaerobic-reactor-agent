"""Reactor status overview with key metrics + radar chart."""

import streamlit as st
import plotly.graph_objects as go
from anaerobic_reactor_agent.models.diagnosis import DiagnosisResult, ParameterStatus

PARAMETER_NAMES_CN = {
    "ph": "pH", "temperature": "温度", "vfa": "VFA",
    "alkalinity": "碱度", "orp": "ORP", "biogas_production": "产气量",
    "methane_content": "甲烷含量", "olr": "OLR", "hrt": "HRT",
    "nh3_n": "氨氮", "cod_removal_rate": "COD去除率",
    "vfa_alkalinity_ratio": "VFA/碱度比",
}

STATUS_CSS = {
    ParameterStatus.NORMAL: ("🟢 正常运行", "#10b981", "#d1fae5"),
    ParameterStatus.WARNING: ("🟡 注意预警", "#f59e0b", "#fef3c7"),
    ParameterStatus.ALARM: ("🔴 异常报警", "#ef4444", "#fee2e2"),
}


def render_overview_card(result: DiagnosisResult):
    """状态概览：总状态 + 关键指标 + 雷达图。"""
    status = result.overall_status
    label, color, bg = STATUS_CSS[status]

    # ---- Status banner ----
    st.markdown(
        f"""<div style='background:{bg};border-left:5px solid {color};padding:16px 20px;
        border-radius:8px;margin-bottom:16px'>
        <span style='font-size:20px;font-weight:bold;color:{color}'>{label}</span>
        <span style='margin-left:16px;color:#666'>故障 {result.fault_count} 个 · 建议 {len(result.recommendations)} 条</span>
        </div>""",
        unsafe_allow_html=True,
    )

    # ---- Key metrics row ----
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cod = _find_assessment(result, "cod_removal_rate")
        cod_val = f"{cod.current_value}%" if cod else "—"
        cod_delta = None
        if cod:
            if cod.status == ParameterStatus.NORMAL:
                cod_delta = "正常"
            elif cod.status == ParameterStatus.WARNING:
                cod_delta = "偏低"
            else:
                cod_delta = "过低"
        st.metric("COD 去除率", cod_val, delta=cod_delta, delta_color="off" if cod_delta == "正常" else "inverse")

    with col2:
        ratio = _find_assessment(result, "vfa_alkalinity_ratio")
        ratio_val = f"{ratio.current_value:.2f}" if ratio else "—"
        ratio_delta = None
        if ratio:
            if ratio.status == ParameterStatus.NORMAL:
                ratio_delta = "正常 (<0.3)"
            elif ratio.status == ParameterStatus.WARNING:
                ratio_delta = "偏高 (>0.3)"
            else:
                ratio_delta = "危险 (>0.5)"
        st.metric("VFA / 碱度比", ratio_val, delta=ratio_delta, delta_color="off")

    with col3:
        ph = _find_assessment(result, "ph")
        ph_val = f"{ph.current_value}" if ph else "—"
        ph_delta = None
        if ph:
            if ph.status == ParameterStatus.NORMAL:
                ph_delta = "正常"
            elif ph.status == ParameterStatus.WARNING:
                ph_delta = "偏低"
            else:
                ph_delta = "过低"
        st.metric("pH 值", ph_val, delta=ph_delta, delta_color="off" if ph_delta == "正常" else "inverse")

    with col4:
        biogas = _find_assessment(result, "biogas_production")
        bg_val = f"{biogas.current_value} m³/d" if biogas else "—"
        bg_delta = None
        if biogas:
            if biogas.status == ParameterStatus.NORMAL:
                bg_delta = "正常"
            elif biogas.status == ParameterStatus.WARNING:
                bg_delta = "偏低"
            else:
                bg_delta = "过低"
        st.metric("沼气产量", bg_val, delta=bg_delta, delta_color="off" if bg_delta == "正常" else "inverse")

    # ---- Radar chart (collapsible — visual but secondary) ----
    with st.expander("📡 参数健康度雷达图", expanded=False):
        radar_data = []
        for a in result.parameter_assessments:
            cn = PARAMETER_NAMES_CN.get(a.parameter_name, a.parameter_name)
            if a.parameter_name in ("cod_inlet", "cod_outlet", "nh3_n", "reactor_type"):
                continue
            radar_data.append((cn, a.health_score * 100))

        if radar_data:
            labels = [r[0] for r in radar_data]
            values = [r[1] for r in radar_data]

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values, theta=labels,
                fill='toself',
                fillcolor='rgba(16, 185, 129, 0.25)',
                line=dict(color='#10b981', width=2),
                name='健康度 (%)',
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0, 100], ticksuffix="%")),
                height=350,
                margin=dict(l=40, r=40, t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)


def _find_assessment(result: DiagnosisResult, param_name: str):
    for a in result.parameter_assessments:
        if a.parameter_name == param_name:
            return a
    return None
