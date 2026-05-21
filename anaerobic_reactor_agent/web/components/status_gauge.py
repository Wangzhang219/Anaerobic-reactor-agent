"""Parameter-level status display components."""

import streamlit as st
import pandas as pd
from anaerobic_reactor_agent.models.diagnosis import DiagnosisResult, ParameterStatus

PARAMETER_NAMES_CN = {
    "ph": "pH 值",
    "temperature": "温度",
    "cod_inlet": "进水 COD",
    "cod_outlet": "出水 COD",
    "vfa": "VFA 挥发性脂肪酸",
    "alkalinity": "碱度",
    "orp": "ORP 氧化还原电位",
    "biogas_production": "沼气产量",
    "methane_content": "甲烷含量",
    "olr": "有机负荷 OLR",
    "hrt": "水力停留时间 HRT",
    "nh3_n": "氨氮 NH₃-N",
    "cod_removal_rate": "COD 去除率",
    "vfa_alkalinity_ratio": "VFA / 碱度比值",
}


def render_parameter_table(result: DiagnosisResult):
    """Render parameter assessment as a styled dataframe."""

    st.subheader("运行参数逐项评估")

    data = []
    for a in result.parameter_assessments:
        cn_name = PARAMETER_NAMES_CN.get(a.parameter_name, a.parameter_name)
        status_cn = {"normal": "正常", "warning": "预警", "alarm": "报警"}.get(a.status.value, a.status.value)
        data.append({
            "参数": cn_name,
            "当前值": a.current_value,
            "状态": status_cn,
            "严重程度": f"{a.severity_score:.0%}",
            "正常范围": a.normal_range,
            "说明": a.message,
        })

    df = pd.DataFrame(data)

    def color_status(val):
        if val == "正常":
            return "background-color: #10b981; color: white"
        elif val == "预警":
            return "background-color: #f59e0b; color: white"
        elif val == "报警":
            return "background-color: #ef4444; color: white"
        return ""

    styled = df.style.map(color_status, subset=["状态"])
    st.dataframe(styled, use_container_width=True, hide_index=True)
