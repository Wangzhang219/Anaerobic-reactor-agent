"""Fault diagnosis panel — compact, scannable, no fluff."""

import streamlit as st
from anaerobic_reactor_agent.models.diagnosis import DiagnosisResult, FaultSeverity


SEVERITY_LABELS = {
    FaultSeverity.WARNING: "预警",
    FaultSeverity.ALARM: "报警",
    FaultSeverity.CRITICAL: "危急",
}

SEVERITY_EMOJI = {
    FaultSeverity.WARNING: "🟡",
    FaultSeverity.ALARM: "🔴",
    FaultSeverity.CRITICAL: "⛔",
}

SEVERITY_BG = {
    FaultSeverity.WARNING: "#fef3c7",
    FaultSeverity.ALARM: "#fee2e2",
    FaultSeverity.CRITICAL: "#fecaca",
}

FAULT_TYPE_NAMES = {
    "acidification": "反应器酸化",
    "ammonia_inhibition": "氨氮抑制",
    "temperature_shock": "温度冲击",
    "organic_overload": "有机负荷过高",
    "sludge_washout": "污泥流失",
    "toxic_inhibition": "毒性物质抑制",
    "sulfide_inhibition": "硫化物抑制",
    "nutrient_deficiency": "营养元素缺乏",
    "calcium_precipitation": "钙盐沉积",
}

LEVEL_COLORS = {"immediate": "#ef4444", "long_term": "#f59e0b", "preventive": "#3b82f6"}
LEVEL_BADGES = {"immediate": "紧急", "long_term": "长期", "preventive": "预防"}

PARAM_CN = {
    "ph": "pH", "vfa": "VFA", "alkalinity": "碱度",
    "temperature": "温度", "orp": "ORP",
    "biogas_production": "产气量", "methane_content": "甲烷含量",
    "olr": "OLR", "hrt": "HRT",
    "nh3_n": "氨氮", "cod_removal_rate": "COD去除率",
    "vfa_alkalinity_ratio": "VFA/碱度比",
}


def render_diagnosis_panel(result: DiagnosisResult):
    """紧凑、言简意赅的故障诊断展示。"""

    if not result.faults:
        st.success("✅ 未检测到故障，反应器运行状态良好。")
        return

    st.subheader(f"🔍 故障诊断（{len(result.faults)} 项）")

    for fault in result.faults:
        emoji = SEVERITY_EMOJI.get(fault.severity, "")
        label = SEVERITY_LABELS.get(fault.severity, "")
        cn_name = FAULT_TYPE_NAMES.get(fault.fault_type, fault.fault_type)
        bg = SEVERITY_BG.get(fault.severity, "#f8f8f8")
        expanded = fault.severity in (FaultSeverity.ALARM, FaultSeverity.CRITICAL)

        # ---- Compact title line ----
        title = f"{emoji} **{cn_name}** | {label} | 可信度 {fault.confidence:.0%}"
        if fault.severity == FaultSeverity.ALARM:
            title = f"{emoji} ⚠️ **{cn_name}** | {label} | 可信度 {fault.confidence:.0%}"
        elif fault.severity == FaultSeverity.CRITICAL:
            title = f"{emoji} 🚨 **{cn_name}** | {label} | 可信度 {fault.confidence:.0%}"

        with st.expander(title, expanded=expanded):
            # ---- One-line summary + cause (merged, concise) ----
            st.markdown(f"**问题：**{fault.description}")

            if fault.causal_chain:
                # Condense causal chain to one compact line
                chain = fault.causal_chain.replace(" → ", " → ")
                st.caption(f"▸ 因果链：{chain}")

            # ---- Key evidence inline ----
            if fault.evidence:
                params_str = []
                for e in fault.evidence[:5]:  # max 5 items
                    for code, cn in PARAM_CN.items():
                        if e.startswith(code + "="):
                            val = e.split(",")[0].replace(code + "=", "")
                            params_str.append(f"**{cn}**={val}")
                            break
                if params_str:
                    st.caption(f"▸ 异常参数：{'，'.join(params_str)}")

            # ---- Confidence bar compact ----
            st.progress(fault.confidence)

            # ---- Recommendations: immediate first, rest folded ----
            if fault.recommendations:
                immediate = [r for r in fault.recommendations if r.level == "immediate"]
                rest = [r for r in fault.recommendations if r.level != "immediate"]

                if immediate:
                    st.markdown("**立即执行：**")
                    for r in immediate:
                        st.markdown(
                            f"- 🔴 {r.text}"
                        )

                if rest:
                    with st.expander(f"查看其他建议（{len(rest)} 条）", expanded=False):
                        for r in rest:
                            color = LEVEL_COLORS.get(r.level, "#888")
                            badge = LEVEL_BADGES.get(r.level, r.level)
                            st.markdown(
                                f"- <span style='color:{color}'>[{badge}]</span> {r.text}",
                                unsafe_allow_html=True,
                            )
