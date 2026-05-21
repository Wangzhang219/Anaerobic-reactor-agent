"""Parameter input form with Demo mode support."""

import streamlit as st
from datetime import datetime

# Demo data (acidification scenario — showcases all diagnostic features)
DEMO_VALUES = {
    "_ph": 6.2, "_temperature": 35.0, "_cod_inlet": 5000.0, "_cod_outlet": 2500.0,
    "_orp": -250.0, "_vfa": 800.0, "_alkalinity": 1500.0,
    "_biogas": 30.0, "_methane": 55.0, "_olr": 8.0, "_hrt": 12.0, "_nh3_n": 50.0,
    "_reactor_index": 0,
}


def render_parameter_form() -> dict | None:
    """渲染参数输入表单。支持 Demo 数据预填。"""

    # Handle demo trigger
    if st.session_state.pop("_demo_trigger", False):
        for k, v in DEMO_VALUES.items():
            st.session_state[k] = v

    with st.expander("📝 反应器运行参数", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            ph = st.number_input(
                "pH 值", min_value=0.0, max_value=14.0, step=0.1,
                value=st.session_state.get("_ph", 7.0),
                help="最佳 6.8-7.5，<6.5 产甲烷菌活性下降，<6.0 基本停止",
            )
            temperature = st.number_input(
                "温度 (°C)", min_value=0.0, max_value=80.0, step=0.5,
                value=st.session_state.get("_temperature", 35.0),
                help="中温厌氧 30-40°C，日变化不宜超过 2°C",
            )
            cod_inlet = st.number_input(
                "进水 COD (mg/L)", min_value=0.0, step=100.0,
                value=st.session_state.get("_cod_inlet", 5000.0),
            )
            orp = st.number_input(
                "ORP (mV)", min_value=-1000.0, max_value=500.0, step=10.0,
                value=st.session_state.get("_orp", -350.0),
                help="必须 < -300 mV 维持厌氧环境",
            )

        with col2:
            vfa = st.number_input(
                "VFA 挥发性脂肪酸 (mg/L)", min_value=0.0, step=10.0,
                value=st.session_state.get("_vfa", 150.0),
                help="正常 <300，>500 酸化风险高",
            )
            alkalinity = st.number_input(
                "碱度 (mg CaCO₃/L)", min_value=0.0, step=50.0,
                value=st.session_state.get("_alkalinity", 2000.0),
                help="正常 1000-5000，提供缓冲能力抵抗 pH 下降",
            )
            cod_outlet = st.number_input(
                "出水 COD (mg/L)", min_value=0.0, step=10.0,
                value=st.session_state.get("_cod_outlet", 500.0),
                help="去除率应 >70%",
            )
            biogas = st.number_input(
                "沼气产量 (m³/d)", min_value=0.0, step=1.0,
                value=st.session_state.get("_biogas", 50.0),
                help="反映产甲烷菌整体活性",
            )

        with col3:
            methane = st.number_input(
                "甲烷含量 (%)", min_value=0.0, max_value=100.0, step=1.0,
                value=st.session_state.get("_methane", 65.0),
                help="正常 55-70%，<45% 表明产甲烷受抑制",
            )
            olr = st.number_input(
                "OLR 有机负荷 (kg COD/m³·d)", min_value=0.0, step=0.5,
                value=st.session_state.get("_olr", 5.0),
                help="UASB 通常 2-10，过高导致 VFA 积累",
            )
            hrt = st.number_input(
                "HRT 水力停留时间 (h)", min_value=0.0, step=1.0,
                value=st.session_state.get("_hrt", 12.0),
                help="通常 6-48h，过短导致污泥流失",
            )
            nh3_n = st.number_input(
                "氨氮 NH₃-N (mg/L)", min_value=0.0, step=1.0,
                value=st.session_state.get("_nh3_n", 50.0),
                help=">150 mg/L 抑制产甲烷菌",
            )

        reactor_type = st.selectbox(
            "反应器类型",
            ["UASB", "CSTR", "EGSB", "IC", "AnMBR"],
            index=st.session_state.get("_reactor_index", 0),
        )

        submitted = st.button("🔬 开始诊断", type="primary", use_container_width=True)

        if submitted:
            type_map = {
                "UASB": "UASB", "CSTR": "CSTR", "EGSB": "EGSB",
                "IC": "IC", "AnMBR": "AnMBR",
            }
            return {
                "ph": ph, "temperature": temperature,
                "cod_inlet": cod_inlet, "cod_outlet": cod_outlet,
                "vfa": vfa, "alkalinity": alkalinity,
                "orp": orp, "biogas_production": biogas,
                "methane_content": methane, "olr": olr, "hrt": hrt,
                "nh3_n": nh3_n,
                "reactor_type": type_map.get(reactor_type, "UASB"),
                "timestamp": datetime.now(),
            }

    return None
