"""Sidebar — page navigation + LLM config + reactor settings."""

import streamlit as st

def render_sidebar():
    """侧边栏：页面导航 + LLM 配置 + 反应器设置。"""
    with st.sidebar:
        st.header("厌氧反应器智能诊断")

        # ============================================================
        # LLM Configuration
        # ============================================================
        st.subheader("🤖 AI 专家分析（可选）")

        with st.expander("💡 这是什么？", expanded=False):
            st.markdown("""
            在规则引擎诊断完成后，让 AI 用通俗语言：
            - 总结反应器状况
            - 分析故障根本原因
            - 评估潜在风险
            - 给出分步骤操作方案

            不配置也能正常使用。推荐 **DeepSeek**（便宜·国产）。
            """)

        provider = st.selectbox(
            "选择 AI 模型",
            [
                "不使用 AI",
                "DeepSeek（推荐·便宜·国产）",
                "智谱 GLM（国产·中文强）",
                "OpenAI / 兼容接口",
                "Anthropic Claude",
                "Google Gemini",
                "Ollama（本地·免费）",
            ],
            index=0,
        )

        st.session_state.llm_provider_type = None

        if provider == "DeepSeek（推荐·便宜·国产）":
            api_key = st.text_input(
                "API Key", type="password",
                placeholder="sk-xxxxxxxxxxxxxxxx",
                help="https://platform.deepseek.com 注册获取",
                key="ds_key",
            )
            if api_key:
                import os
                os.environ["DEEPSEEK_API_KEY"] = api_key
                st.session_state.api_key_configured = True
                st.session_state.llm_enabled = True
                st.session_state.llm_provider_type = "deepseek"
                st.success("已配置 ✅")

        elif provider == "智谱 GLM（国产·中文强）":
            api_key = st.text_input(
                "API Key", type="password",
                placeholder="xxxxxxxxxx.xxxxxxxxxx",
                help="https://open.bigmodel.cn 注册获取",
                key="zhipu_key",
            )
            if api_key:
                import os
                os.environ["ZHIPU_API_KEY"] = api_key
                st.session_state.api_key_configured = True
                st.session_state.llm_enabled = True
                st.session_state.llm_provider_type = "zhipu"
                st.success("已配置 ✅")

        elif provider == "OpenAI / 兼容接口":
            api_key = st.text_input(
                "API Key", type="password", placeholder="sk-...",
                key="oai_key",
            )
            base_url = st.text_input(
                "接口地址（可选）", placeholder="https://api.openai.com/v1",
                key="oai_url",
            )
            if api_key:
                import os
                os.environ["OPENAI_API_KEY"] = api_key
                if base_url:
                    os.environ["OPENAI_BASE_URL"] = base_url
                st.session_state.api_key_configured = True
                st.session_state.llm_enabled = True
                st.session_state.llm_provider_type = "openai"
                st.success("已配置 ✅")

        elif provider == "Anthropic Claude":
            api_key = st.text_input(
                "API Key", type="password", placeholder="sk-ant-...",
                key="claude_key",
            )
            if api_key:
                import os
                os.environ["ANTHROPIC_API_KEY"] = api_key
                st.session_state.api_key_configured = True
                st.session_state.llm_enabled = True
                st.session_state.llm_provider_type = "claude"
                st.success("已配置 ✅")

        elif provider == "Google Gemini":
            api_key = st.text_input(
                "API Key", type="password", placeholder="AIza...",
                key="gemini_key",
            )
            if api_key:
                import os
                os.environ["GEMINI_API_KEY"] = api_key
                st.session_state.api_key_configured = True
                st.session_state.llm_enabled = True
                st.session_state.llm_provider_type = "gemini"
                st.success("已配置 ✅")

        elif provider == "Ollama（本地·免费）":
            base_url = st.text_input(
                "Ollama 地址",
                value="http://localhost:11434/v1",
                key="ollama_url",
            )
            model = st.text_input("模型名称", value="qwen3:8b", key="ollama_model")
            st.caption("需先安装 Ollama 并运行 `ollama pull qwen3:8b`")
            import os
            os.environ["OLLAMA_BASE_URL"] = base_url
            st.session_state.api_key_configured = True
            st.session_state.llm_enabled = True
            st.session_state.llm_provider_type = "ollama"
            st.success("已配置 ✅")

        else:
            st.session_state.llm_enabled = False

        st.divider()

        # ============================================================
        # Reactor Settings
        # ============================================================
        st.subheader("⚙️ 反应器设置")
        reactor_name = st.text_input("反应器编号", value="1号反应器")
        if reactor_name:
            st.session_state.reactor_name = reactor_name

        st.divider()
        st.caption("v0.2.0 | 25 tests passed")
