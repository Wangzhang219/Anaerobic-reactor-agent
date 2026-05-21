"""History page — trend analysis and past diagnosis review."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from anaerobic_reactor_agent.models.diagnosis import ParameterStatus


def render_history():
    """Render the historical analysis page."""
    st.header("历史趋势分析")

    # CSV upload
    uploaded_file = st.file_uploader(
        "上传历史运行数据（CSV 格式）",
        type=["csv"],
        help="CSV 需包含以下列：timestamp, ph, temperature, cod_inlet, cod_outlet, vfa, alkalinity 等",
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        st.subheader("上传的数据")
        st.dataframe(df, use_container_width=True)

        st.subheader("参数趋势图")
        param_options = [c for c in df.columns if c != "timestamp"]
        selected_params = st.multiselect(
            "选择要展示的参数",
            param_options,
            default=param_options[:4] if len(param_options) >= 4 else param_options,
        )

        if selected_params:
            fig = go.Figure()
            for param in selected_params:
                fig.add_trace(go.Scatter(
                    x=df["timestamp"] if "timestamp" in df.columns else df.index,
                    y=df[param],
                    mode="lines+markers",
                    name=param,
                ))
            fig.update_layout(
                title="运行参数趋势变化",
                xaxis_title="时间",
                yaxis_title="数值",
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Session history
    if st.session_state.history:
        st.divider()
        st.subheader(f"本次会话诊断记录（{len(st.session_state.history)} 条）")

        history_data = []
        for i, result in enumerate(st.session_state.history):
            status_cn = {"normal": "正常", "warning": "预警", "alarm": "报警"}.get(
                result.overall_status.value, result.overall_status.value
            )
            history_data.append({
                "序号": i + 1,
                "时间": result.timestamp.strftime("%H:%M:%S"),
                "状态": status_cn,
                "故障数": result.fault_count,
                "建议数": len(result.recommendations),
            })

        history_df = pd.DataFrame(history_data)

        def color_status(val):
            if val == "正常":
                return "background-color: #10b981; color: white"
            elif val == "预警":
                return "background-color: #f59e0b; color: white"
            elif val == "报警":
                return "background-color: #ef4444; color: white"
            return ""

        styled = history_df.style.map(color_status, subset=["状态"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        if st.button("清空会话记录"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("在「诊断面板」页运行诊断后，记录将显示在这里。")
