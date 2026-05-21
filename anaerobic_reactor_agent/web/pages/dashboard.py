"""Main dashboard page — parameter input, diagnosis display, and report export."""

import streamlit as st
from datetime import datetime
import base64

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
    """Render the main dashboard page."""
    engine = get_engine()

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
        st.info("请在上方填写反应器运行参数，然后点击「开始诊断」按钮。")
        return

    st.divider()
    st.header("诊断结果")

    render_overview_card(result)
    render_parameter_table(result)
    st.divider()
    render_diagnosis_panel(result)
    st.divider()
    render_recommendation_list(result)

    if result.llm_analysis:
        with st.expander(f"AI 专家分析（由 {result.llm_model or '未知模型'} 生成）", expanded=True):
            st.markdown(result.llm_analysis)
    elif st.session_state.llm_enabled:
        st.warning("AI 分析未能完成——可能是 API Key 无效或网络问题。规则引擎诊断结果仍然可用。")
    else:
        with st.expander("AI 专家分析（未启用）", expanded=False):
            st.markdown("""
            **AI 专家分析**能够在规则引擎诊断的基础上，提供一份用通俗语言撰写的"专家级分析报告"，包括：
            - 反应器状况的通俗总结
            - 故障根本原因分析
            - 潜在风险评估
            - 分步骤操作方案

            **如何启用？** 在左侧边栏 → 选择 AI 模型 → 填入 API Key 即可。

            推荐使用 **DeepSeek**（国产、便宜、注册送免费额度）。
            """)

    # Export report
    st.divider()
    _render_export_section(result)


def _render_export_section(result):
    """Render the report export section."""
    st.subheader("导出诊断报告")

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
    """Generate a beautiful HTML report from diagnosis result."""
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
            <p><em>因果链: {f.causal_chain or "N/A"}</em></p>
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
    """Attempt LLM enrichment."""
    from anaerobic_reactor_agent.llm.factory import create_provider
    try:
        provider_type = st.session_state.get("llm_provider_type") or None
        provider = create_provider(provider_type=provider_type)
        if provider:
            result.llm_analysis = provider.analyze(result)
            result.llm_model = provider.model_name
    except Exception as e:
        st.warning(f"AI 分析不可用：{e}")
