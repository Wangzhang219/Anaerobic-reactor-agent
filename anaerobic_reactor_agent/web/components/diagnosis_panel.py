"""Fault diagnosis panel displaying detected faults in plain Chinese."""

import streamlit as st
from anaerobic_reactor_agent.models.diagnosis import DiagnosisResult, FaultSeverity


SEVERITY_LABELS = {
    FaultSeverity.WARNING: "注意预警",
    FaultSeverity.ALARM: "异常报警",
    FaultSeverity.CRITICAL: "严重危急",
}

SEVERITY_EMOJI = {
    FaultSeverity.WARNING: "🟡",
    FaultSeverity.ALARM: "🔴",
    FaultSeverity.CRITICAL: "⛔",
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

# Human-readable rule name mapping (code → plain Chinese)
RULE_NAME_CN = {
    "acidification_classic": "典型酸化模式（VFA高+pH低+VFA/碱度比超标）",
    "acidification_early_warning": "酸化早期预警（VFA上升+VFA/碱度比偏高，pH尚正常）",
    "ammonia_inhibition": "氨氮抑制模式（NH₃-N高+甲烷含量低+pH偏高）",
    "temperature_shock": "温度冲击模式（温度偏离中温范围+产气量下降）",
    "organic_overload": "有机负荷过高模式（OLR超限+COD去除率下降+VFA上升）",
    "sludge_washout": "污泥流失模式（HRT过短+COD去除率下降）",
    "toxic_inhibition": "毒性抑制模式（产气量骤降+甲烷含量低+pH下降）",
    "sulfide_inhibition": "硫化物抑制模式（甲烷低+产气少+pH偏低）",
    "nutrient_deficiency": "营养缺乏模式（COD去除率低+VFA上升+产气不足）",
    "calcium_precipitation": "钙沉积模式（碱度高+COD去除率低+pH偏高）",
}

LEVEL_COLORS = {"immediate": "#ef4444", "long_term": "#f59e0b", "preventive": "#3b82f6"}
LEVEL_NAMES = {"immediate": "紧急处理", "long_term": "长期措施", "preventive": "预防建议"}

# Parameter name mapping for evidence messages
PARAM_CN = {
    "ph": "pH值", "vfa": "挥发性脂肪酸(VFA)", "alkalinity": "碱度",
    "temperature": "温度", "orp": "氧化还原电位(ORP)",
    "biogas_production": "沼气产量", "methane_content": "甲烷含量",
    "olr": "有机负荷(OLR)", "hrt": "水力停留时间(HRT)",
    "nh3_n": "氨氮(NH₃-N)", "cod_removal_rate": "COD去除率",
    "vfa_alkalinity_ratio": "VFA/碱度比值",
}


def render_diagnosis_panel(result: DiagnosisResult):
    """以通俗中文展示故障诊断结果。"""

    if not result.faults:
        st.success("未检测到故障，反应器运行状态良好。")
        return

    st.subheader(f"故障诊断（共发现 {len(result.faults)} 个问题）")

    for fault in result.faults:
        emoji = SEVERITY_EMOJI.get(fault.severity, "⚪")
        label = SEVERITY_LABELS.get(fault.severity, "未知")
        cn_name = FAULT_TYPE_NAMES.get(fault.fault_type, fault.fault_type)

        # Default to expanded for ALARM and CRITICAL
        expanded = fault.severity in (FaultSeverity.ALARM, FaultSeverity.CRITICAL)

        with st.expander(
            f"{emoji} {cn_name} — {label}（可信度 {fault.confidence:.0%}）",
            expanded=expanded,
        ):
            # ---- 问题说明 ----
            st.markdown("### 这是什么问题？")
            st.write(fault.description)

            # ---- 为什么发生 ----
            if fault.causal_chain:
                st.markdown("### 为什么会发生？（因果链）")
                # Split causal chain into steps for readability
                steps = [s.strip() for s in fault.causal_chain.replace("→", "→").split("→")]
                chain_text = "  →  ".join(steps)
                st.info(chain_text)

            # ---- 判断依据 ----
            st.markdown("### 判断依据（系统是如何发现这个问题的）")
            # Show matched rules in plain Chinese
            with st.container(border=True):
                for r in fault.matched_rules:
                    cn_desc = RULE_NAME_CN.get(r, r)
                    st.caption(f"触发规则：{cn_desc}")

            # ---- 数据证据 ----
            if fault.evidence:
                st.markdown("### 哪些数据出现了异常？")
                # Filter and rewrite evidence into plain language
                seen_params = set()
                for e in fault.evidence:
                    # Parse evidence (format: "param_name=value unit, message")
                    for code, cn in PARAM_CN.items():
                        if e.startswith(code + "="):
                            if code not in seen_params:
                                seen_params.add(code)
                                # Extract the message part after the comma
                                parts = e.split(",", 1)
                                if len(parts) == 2:
                                    value_part = parts[0].replace(code + "=", "")
                                    st.markdown(
                                        f"- **{cn}**：当前值 `{value_part}`，{parts[1]}"
                                    )
                                else:
                                    st.markdown(f"- **{cn}**：{e}")
                            break
                    else:
                        st.markdown(f"- {e}")

            # ---- 置信度 ----
            confidence_pct = fault.confidence * 100
            if confidence_pct >= 80:
                conf_label = "高度可信 —— 多个指标同时指向此问题"
            elif confidence_pct >= 50:
                conf_label = "较可信 —— 主要指标符合，建议进一步确认"
            else:
                conf_label = "需关注 —— 部分指标异常，建议持续观察"
            st.progress(fault.confidence, text=f"可信度：{confidence_pct:.0f}%（{conf_label}）")

            # ---- 处理建议 ----
            if fault.recommendations:
                st.markdown("### 针对此问题的处理建议")
                for i, rec in enumerate(fault.recommendations, 1):
                    color = LEVEL_COLORS.get(rec.level, "#888")
                    level_name = LEVEL_NAMES.get(rec.level, rec.level)
                    st.markdown(
                        f"{i}. <span style='color:{color};font-weight:bold'>[{level_name}]</span> {rec.text}",
                        unsafe_allow_html=True,
                    )
