"""Dashboard — parameter input → diagnosis → history, all in one page."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from anaerobic_reactor_agent.engine.rule_engine import RuleEngine
from anaerobic_reactor_agent.models.reactor_state import ReactorParameters
from anaerobic_reactor_agent.utils.validators import validate_reactor_params
from anaerobic_reactor_agent.web.components.parameter_form import render_parameter_form
from anaerobic_reactor_agent.web.components.overview_card import render_overview_card
from anaerobic_reactor_agent.web.components.diagnosis_panel import render_diagnosis_panel
from anaerobic_reactor_agent.web.components.recommendation_list import render_recommendation_list
from anaerobic_reactor_agent.web.components.status_gauge import render_parameter_table


@st.cache_resource
def get_engine():
    return RuleEngine()


def render_dashboard():
    """单页布局：参数输入 → 诊断结果 → 历史趋势。"""
    engine = get_engine()

    # ================================================================
    # Section 1: Parameter Input
    # ================================================================
    params_data = render_parameter_form()

    if params_data is not None:
        with st.spinner("正在运行诊断分析..."):
            params = ReactorParameters(**params_data)
            warnings = validate_reactor_params(params)
            if warnings:
                for w in warnings:
                    st.warning(w)
            result = engine.diagnose(params)

            if st.session_state.llm_enabled:
                _run_llm_analysis(result)

            st.session_state.reactor_params = params_data
            st.session_state.diagnosis_result = result
            st.session_state.history.append(result)

    result = st.session_state.diagnosis_result
    if result is None:
        # ---- Initial state: welcome + guide ----
        st.divider()
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.markdown("""
            ### 👋 欢迎使用厌氧反应器智能诊断系统

            本系统能够：

            - 📊 **实时诊断** — 输入运行参数，自动识别 9 种常见故障
            - 🧠 **AI 专家分析** — 可选启用大模型，获得专家级文字解读
            - 📈 **趋势分析** — 上传历史 CSV 数据，查看参数变化趋势
            - 📥 **报告导出** — 一键下载 HTML 诊断报告

            **开始使用：** 展开上方「反应器运行参数」表单，填写参数后点击「开始诊断」按钮。
            """)
        with col_b:
            st.markdown("")
            st.markdown("")
            if st.button("🚀 快速体验（Demo 数据）", use_container_width=True, type="primary"):
                # Auto-fill with acidification demo data
                st.session_state._demo_trigger = True
                st.rerun()
        _render_history_section()
        return

    # ================================================================
    # Section 2: Overview & Key Metrics
    # ================================================================
    st.divider()
    render_overview_card(result)

    # ================================================================
    # Section 3: Parameter Table (collapsible — secondary info)
    # ================================================================
    with st.expander("📊 参数明细表（点击展开）", expanded=False):
        render_parameter_table(result)

    # ================================================================
    # Section 4: Fault Diagnosis (primary info — always visible)
    # ================================================================
    st.divider()
    render_diagnosis_panel(result)

    # ================================================================
    # Section 5: Overall Recommendations (collapsed if many)
    # ================================================================
    if result.recommendations:
        st.divider()
        # Show top 5 immediate actions prominently
        immediate = [r for r in result.recommendations if r.level == "immediate"][:5]
        rest_recs = [r for r in result.recommendations if r not in immediate]

        if immediate:
            st.subheader("⚡ 优先处理事项")
            for i, r in enumerate(immediate, 1):
                st.markdown(f"{i}. 🔴 {r.text}")

        if rest_recs:
            with st.expander(f"📋 完整建议清单（共 {len(result.recommendations)} 条）", expanded=False):
                render_recommendation_list(result)

    # ================================================================
    # Section 6: LLM Analysis (prominent when available)
    # ================================================================
    st.divider()
    if result.llm_analysis:
        with st.expander(f"🤖 AI 专家分析（{result.llm_model or '未知模型'}）", expanded=True):
            st.markdown(result.llm_analysis)
    elif st.session_state.llm_enabled:
        st.warning("AI 分析未能完成——可能是 API Key 无效或网络问题。")
    else:
        st.info("💡 在左侧边栏配置 AI 模型（推荐 DeepSeek），可获得专家级文字分析。")

    # ================================================================
    # Section 7: Export
    # ================================================================
    st.divider()
    _render_export_section(result)

    # ================================================================
    # Section 8: History & Trends (bottom, collapsible)
    # ================================================================
    st.divider()
    _render_history_section()


# ====================================================================
# Helper functions
# ====================================================================

def _render_history_section():
    """历史诊断记录 + CSV趋势分析（折叠版——在dashboard底部使用）。"""
    with st.expander("📈 历史记录与趋势分析", expanded=False):
        _render_history_body()


def _render_history_section_full():
    """历史诊断记录 + CSV趋势分析（全页版——侧边栏导航使用）。"""
    st.header("📈 历史记录与趋势分析")
    _render_history_body()


def _render_history_body():
    """历史记录的共享内容。"""
    tab1, tab2 = st.tabs(["本次会话记录", "上传CSV趋势分析"])

    with tab1:
        if st.session_state.history:
            history_data = []
            for i, result in enumerate(st.session_state.history):
                status_cn = {"normal": "正常", "warning": "预警", "alarm": "报警"}.get(
                    result.overall_status.value, result.overall_status.value
                )
                faults_str = ", ".join(
                    ["酸化" if f == "acidification" else
                     "氨抑制" if f == "ammonia_inhibition" else
                     "温度冲击" if f == "temperature_shock" else
                     "过载" if f == "organic_overload" else
                     "污泥流失" if f == "sludge_washout" else
                     "毒性" if f == "toxic_inhibition" else
                     "硫化物" if f == "sulfide_inhibition" else
                     "缺营养" if f == "nutrient_deficiency" else
                     "钙沉积" if f == "calcium_precipitation" else f
                     for f in [fault.fault_type for fault in result.faults]
                    ]) or "—"

                history_data.append({
                    "#": i + 1,
                    "时间": result.timestamp.strftime("%m-%d %H:%M"),
                    "状态": status_cn,
                    "故障": faults_str,
                    "建议数": len(result.recommendations),
                })

            df = pd.DataFrame(history_data)

            def color_status(val):
                if val == "正常": return "background-color: #10b981; color: white"
                elif val == "预警": return "background-color: #f59e0b; color: white"
                elif val == "报警": return "background-color: #ef4444; color: white"
                return ""

            styled = df.style.map(color_status, subset=["状态"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("🗑️ 清空记录", use_container_width=True):
                    st.session_state.history = []
                    st.rerun()
        else:
            st.info("运行诊断后，记录将自动保存在这里。")

    with tab2:
        uploaded = st.file_uploader(
            "上传历史运行数据（CSV）",
            type=["csv"],
            help="CSV 需包含 timestamp, ph, temperature, cod_inlet, cod_outlet, vfa, alkalinity 等列",
        )
        if uploaded:
            df = pd.read_csv(uploaded)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

            st.dataframe(df.head(20), use_container_width=True)

            params = [c for c in df.columns if c != "timestamp"]
            selected = st.multiselect("选择参数", params, default=params[:4])

            if selected:
                fig = go.Figure()
                for p in selected:
                    fig.add_trace(go.Scatter(
                        x=df["timestamp"], y=df[p],
                        mode="lines+markers", name=p,
                    ))
                fig.update_layout(
                    title="运行参数趋势",
                    xaxis_title="时间", yaxis_title="数值",
                    hovermode="x unified", height=350,
                    margin=dict(l=20, r=20, t=40, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)


def _render_export_section(result):
    """导出按钮。"""
    st.subheader("📥 导出报告")

    html_report = _generate_html_report(result)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="下载 HTML 诊断报告",
            data=html_report,
            file_name=f"reactor_diagnosis_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            use_container_width=True,
        )
    with col2:
        json_data = result.model_dump_json(indent=2)
        st.download_button(
            label="下载 JSON 原始数据",
            data=json_data,
            file_name=f"reactor_diagnosis_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )


def _generate_html_report(result) -> str:
    """生成 HTML 诊断报告。"""
    status_cn = {"normal": "正常运行", "warning": "注意预警", "alarm": "异常报警"}
    severity_cn = {"warning": "预警", "alarm": "报警", "critical": "危急"}
    fault_cn = {
        "acidification": "酸化", "ammonia_inhibition": "氨抑制",
        "temperature_shock": "温度冲击", "organic_overload": "有机负荷过高",
        "sludge_washout": "污泥流失", "toxic_inhibition": "毒性抑制",
        "sulfide_inhibition": "硫化物抑制", "nutrient_deficiency": "营养缺乏",
        "calcium_precipitation": "钙沉积",
    }
    level_cn = {"immediate": "紧急处理", "long_term": "长期措施", "preventive": "预防建议"}

    rows = ""
    for a in result.parameter_assessments:
        s_color = {"normal": "#10b981", "warning": "#f59e0b", "alarm": "#ef4444"}.get(a.status.value, "#888")
        rows += f"<tr><td>{a.parameter_name}</td><td>{a.current_value}</td><td style='color:{s_color}'>{a.status.value}</td><td>{a.health_score:.0%}</td><td>{a.normal_range}</td></tr>"

    fault_html = ""
    for f in result.faults:
        cn = fault_cn.get(f.fault_type, f.fault_type)
        sev = severity_cn.get(f.severity.value, f.severity.value)
        recs = ""
        for r in f.recommendations:
            lvl = level_cn.get(r.level, r.level)
            recs += f"<li><span style='color:#ef4444'>[{lvl}]</span> {r.text}</li>"
        fault_html += f"""
        <div style='border:1px solid #ddd;padding:15px;margin:10px 0;border-radius:8px'>
            <h3>[{sev}] {cn} (置信度: {f.confidence:.0%})</h3>
            <p>{f.description}</p>
            <p><em>因果链: {f.causal_chain or 'N/A'}</em></p>
            <ul>{recs}</ul>
        </div>"""

    all_recs = ""
    for r in result.recommendations:
        lvl = level_cn.get(r.level, r.level)
        all_recs += f"<li><span style='color:#ef4444'>[{lvl}]</span> {r.text}</li>"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>厌氧反应器诊断报告</title>
<style>
body{{font-family:'Microsoft YaHei',sans-serif;max-width:900px;margin:20px auto;padding:20px;background:#f5f5f5}}
.card{{background:white;border-radius:12px;padding:25px;margin:15px 0;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
h1,h2{{color:#1a1a2e}} h2{{border-bottom:2px solid #10b981;padding-bottom:8px}}
table{{width:100%;border-collapse:collapse}} th{{background:#1a1a2e;color:white;padding:10px}} td{{padding:8px;border-bottom:1px solid #ddd}}
.status-{result.overall_status.value}{{display:inline-block;padding:4px 16px;border-radius:20px;color:white;font-weight:bold;font-size:18px;background:{'#10b981' if result.overall_status.value == 'normal' else '#f59e0b' if result.overall_status.value == 'warning' else '#ef4444'}}}
</style></head>
<body>
<div class="card">
<h1>厌氧反应器智能诊断报告</h1>
<p>生成时间: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | 反应器编号: {result.reactor_id or 'N/A'}</p>
<h2>总体状态: <span class="status-{result.overall_status.value}">{status_cn.get(result.overall_status.value, result.overall_status.value)}</span></h2>
<p>检测到故障: {result.fault_count} 个 | 操作建议: {len(result.recommendations)} 条</p>
</div>
<div class="card">
<h2>参数评估表</h2>
<table><tr><th>参数</th><th>当前值</th><th>状态</th><th>健康度</th><th>正常范围</th></tr>{rows}</table>
</div>
<div class="card">
<h2>故障诊断</h2>
{fault_html if fault_html else '<p style="color:#10b981">未检测到故障，反应器运行正常。</p>'}
</div>
<div class="card">
<h2>操作建议汇总</h2>
<ol>{all_recs}</ol>
</div>
<div class="card" style="text-align:center;color:#888;font-size:12px">
<p>本报告由厌氧反应器智能诊断系统自动生成 | v0.2.0</p>
</div>
</body></html>"""


def _run_llm_analysis(result):
    """调用大模型进行专家分析。"""
    from anaerobic_reactor_agent.llm.factory import create_provider
    try:
        provider_type = st.session_state.get("llm_provider_type") or None
        provider = create_provider(provider_type=provider_type)
        if provider:
            result.llm_analysis = provider.analyze(result)
            result.llm_model = provider.model_name
    except Exception as e:
        st.warning(f"AI 分析不可用：{e}")
