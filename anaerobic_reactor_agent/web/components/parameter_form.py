"""Parameter input form for reactor data."""

import streamlit as st
from datetime import datetime


def render_parameter_form() -> dict | None:
    """Render the parameter input form. Returns a dict of values or None if form not submitted."""

    with st.expander("反应器运行参数", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            ph = st.number_input("pH 值", min_value=0.0, max_value=14.0, value=7.0, step=0.1,
                                 help="最佳范围：6.8 - 7.5，低于 6.5 产甲烷菌活性下降，低于 6.0 基本停止")
            temperature = st.number_input("温度 (°C)", min_value=0.0, max_value=80.0, value=35.0, step=0.5,
                                          help="中温厌氧：30 - 40°C；高温厌氧：50 - 60°C。日变化不宜超过 2°C")
            cod_inlet = st.number_input("进水 COD (mg/L)", min_value=0.0, value=5000.0, step=100.0,
                                        help="化学需氧量，反映进水有机负荷")
            orp = st.number_input("ORP 氧化还原电位 (mV)", min_value=-1000.0, max_value=500.0, value=-350.0, step=10.0,
                                  help="必须 < -300 mV 才能维持厌氧环境")

        with col2:
            vfa = st.number_input("VFA 挥发性脂肪酸 (mg/L)", min_value=0.0, value=150.0, step=10.0,
                                  help="正常 < 300 mg/L；> 500 mg/L 酸化风险高")
            alkalinity = st.number_input("碱度 (mg CaCO₃/L)", min_value=0.0, value=2000.0, step=50.0,
                                         help="正常 1000 - 5000，提供缓冲能力，抵抗 pH 下降")
            cod_outlet = st.number_input("出水 COD (mg/L)", min_value=0.0, value=500.0, step=10.0,
                                         help="与进水 COD 对比计算去除率，正常应 > 70%")
            biogas = st.number_input("沼气产量 (m³/d)", min_value=0.0, value=50.0, step=1.0,
                                     help="反映产甲烷菌整体活性")

        with col3:
            methane = st.number_input("甲烷含量 (%)", min_value=0.0, max_value=100.0, value=65.0, step=1.0,
                                      help="正常 55 - 70%，低于 45% 表明产甲烷受抑制")
            olr = st.number_input("有机负荷 OLR (kg COD/m³·d)", min_value=0.0, value=5.0, step=0.5,
                                  help="UASB 通常 2 - 10；过高会导致 VFA 积累和酸化")
            hrt = st.number_input("水力停留时间 HRT (h)", min_value=0.0, value=12.0, step=1.0,
                                  help="通常 6 - 48h；过短会导致污泥流失")
            nh3_n = st.number_input("氨氮 NH₃-N (mg/L) [可选]", min_value=0.0, value=50.0, step=1.0,
                                    help="游离氨 > 150 mg/L 会抑制产甲烷菌")

        reactor_type = st.selectbox(
            "反应器类型",
            ["UASB（上流式厌氧污泥床）", "CSTR（全混式）", "EGSB（膨胀颗粒污泥床）", "IC（内循环）", "AnMBR（厌氧膜生物反应器）"],
            index=0,
        )

        submitted = st.button("开始诊断", type="primary", use_container_width=True)

        if submitted:
            type_map = {
                "UASB（上流式厌氧污泥床）": "UASB",
                "CSTR（全混式）": "CSTR",
                "EGSB（膨胀颗粒污泥床）": "EGSB",
                "IC（内循环）": "IC",
                "AnMBR（厌氧膜生物反应器）": "AnMBR",
            }
            return {
                "ph": ph,
                "temperature": temperature,
                "cod_inlet": cod_inlet,
                "cod_outlet": cod_outlet,
                "vfa": vfa,
                "alkalinity": alkalinity,
                "orp": orp,
                "biogas_production": biogas,
                "methane_content": methane,
                "olr": olr,
                "hrt": hrt,
                "nh3_n": nh3_n,
                "reactor_type": type_map.get(reactor_type, "UASB"),
                "timestamp": datetime.now(),
            }

    return None
