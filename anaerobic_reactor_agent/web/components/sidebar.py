"""Sidebar component — LLM configuration with clear onboarding guide."""

import streamlit as st


def render_sidebar():
    """Render sidebar with LLM setup guide and reactor settings."""
    with st.sidebar:
        st.header("系统配置")

        # ============================================================
        # LLM Section — with clear explanation of what it does
        # ============================================================
        st.subheader("AI 专家分析 (可选)")

        with st.expander("这是什么？点开查看说明", expanded=False):
            st.markdown("""
            **AI 专家分析**会在规则引擎诊断的基础上，让大语言模型（LLM）：
            1. 用通俗语言**总结**反应器当前状况
            2. 深入分析故障的**根本原因**
            3. 评估如果不处理的**潜在风险**
            4. 给出**分步骤的操作方案**

            **不需要 AI 也能正常使用**——规则引擎已经能独立完成诊断。
            启用 AI 只是额外获得一份"专家级的文字解读"。

            **如何使用：**
            1. 在下拉菜单中选择一个 AI 提供商
            2. 去对应网站注册获取 API Key（通常免费额度足够测试）
            3. 粘贴 API Key 即可使用
            """)

        provider = st.selectbox(
            "选择 AI 模型",
            [
                "不使用 AI 分析",
                "DeepSeek（推荐·便宜·国产）",
                "智谱 GLM（国产·中文强）",
                "OpenAI / 兼容接口",
                "Anthropic Claude",
                "Google Gemini",
                "Ollama（本地·免费·无需联网）",
            ],
            index=0,
        )

        st.session_state.llm_provider_type = None

        # ---- DeepSeek ----
        if provider == "DeepSeek（推荐·便宜·国产）":
            st.info("**推荐！** DeepSeek 目前最便宜，注册送免费额度，中文能力强。")
            api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                help="去 https://platform.deepseek.com 注册，在「API Keys」页面创建",
                key="ds_key",
            )
            model = st.selectbox(
                "模型",
                ["deepseek-chat（通用）", "deepseek-reasoner（深度推理）"],
                help="chat：日常分析；reasoner：更深入的推理，但较慢",
                key="ds_model",
            )
            if api_key:
                import os
                os.environ["DEEPSEEK_API_KEY"] = api_key
                st.session_state.api_key_configured = True
                st.session_state.llm_enabled = True
                st.session_state.llm_provider_type = "deepseek"
                st.success("已配置 DeepSeek，诊断时将自动调用 AI 分析")

        # ---- ZhipuAI ----
        elif provider == "智谱 GLM（国产·中文强）":
            st.info("智谱 AI 的 GLM 系列模型，中文理解和生成能力优秀。")
            api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="xxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxx",
                help="去 https://open.bigmodel.cn 注册，在「API Keys」页面创建",
                key="zhipu_key",
            )
            model = st.selectbox(
                "模型",
                ["glm-4-flash（快速·免费）", "glm-4（标准）", "glm-4-plus（增强）"],
                help="flash：免费轻量；标准：日常使用；plus：最强推理",
                key="zhipu_model",
            )
            if api_key:
                import os
                os.environ["ZHIPU_API_KEY"] = api_key
                st.session_state.api_key_configured = True
                st.session_state.llm_enabled = True
                st.session_state.llm_provider_type = "zhipu"
                st.success("已配置智谱 GLM，诊断时将自动调用 AI 分析")

        # ---- OpenAI ----
        elif provider == "OpenAI / 兼容接口":
            st.info("使用 OpenAI 官方 API 或任何兼容接口（如国内中转、OneAPI 等）。")
            api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                help="OpenAI 官方 Key 或兼容接口的 Key",
                key="oai_key",
            )
            base_url = st.text_input(
                "接口地址（可选，用官方 API 则留空）",
                placeholder="https://api.openai.com/v1",
                help="如果使用中转服务或第三方兼容接口，填写对应的地址",
                key="oai_url",
            )
            model = st.text_input(
                "模型名称",
                value="gpt-4o",
                help="gpt-4o / gpt-4o-mini / 或其他兼容模型名",
                key="oai_model",
            )
            if api_key:
                import os
                os.environ["OPENAI_API_KEY"] = api_key
                if base_url:
                    os.environ["OPENAI_BASE_URL"] = base_url
                st.session_state.api_key_configured = True
                st.session_state.llm_enabled = True
                st.session_state.llm_provider_type = "openai"
                st.success("已配置 OpenAI，诊断时将自动调用 AI 分析")

        # ---- Claude ----
        elif provider == "Anthropic Claude":
            st.info("Claude 擅长深度分析和长文本推理，但需国外网络和付费。")
            api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                help="去 https://console.anthropic.com 注册获取",
                key="claude_key",
            )
            model = st.selectbox(
                "模型",
                ["claude-sonnet-4-6（推荐）", "claude-opus-4-7（最强）", "claude-haiku-4-5（最快）"],
                key="claude_model",
            )
            if api_key:
                import os
                os.environ["ANTHROPIC_API_KEY"] = api_key
                st.session_state.api_key_configured = True
                st.session_state.llm_enabled = True
                st.session_state.llm_provider_type = "claude"
                st.success("已配置 Claude，诊断时将自动调用 AI 分析")

        # ---- Gemini ----
        elif provider == "Google Gemini":
            st.info("Google Gemini，免费额度较大，但可能需要国外网络。")
            api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="AIza...",
                help="去 https://aistudio.google.com 获取 API Key",
                key="gemini_key",
            )
            model = st.selectbox(
                "模型",
                ["gemini-2.5-flash（推荐）", "gemini-2.5-pro（推理增强）", "gemini-2.0-flash"],
                key="gemini_model",
            )
            if api_key:
                import os
                os.environ["GEMINI_API_KEY"] = api_key
                st.session_state.api_key_configured = True
                st.session_state.llm_enabled = True
                st.session_state.llm_provider_type = "gemini"
                st.success("已配置 Gemini，诊断时将自动调用 AI 分析")

        # ---- Ollama ----
        elif provider == "Ollama（本地·免费·无需联网）":
            st.info("使用本机运行的大模型，**完全免费、无需联网、数据不外传**。需先安装 Ollama。")
            base_url = st.text_input(
                "Ollama 地址",
                value="http://localhost:11434/v1",
                help="一般不用改，除非 Ollama 跑在其他机器上",
                key="ollama_url",
            )
            model = st.text_input(
                "模型名称",
                value="qwen3:8b",
                help="先运行 'ollama pull qwen3:8b' 下载模型",
                key="ollama_model",
            )
            st.caption("安装步骤：https://ollama.com 下载 → 安装 → 终端运行 `ollama pull qwen3:8b`")
            import os
            os.environ["OLLAMA_BASE_URL"] = base_url
            st.session_state.api_key_configured = True
            st.session_state.llm_enabled = True
            st.session_state.llm_provider_type = "ollama"
            st.success("已配置 Ollama，诊断时将自动调用本地 AI 分析")

        else:
            st.session_state.llm_enabled = False

        st.divider()

        # ============================================================
        # Reactor settings
        # ============================================================
        st.subheader("反应器设置")
        reactor_name = st.text_input("反应器编号 / 名称", value="1号反应器")
        if reactor_name:
            st.session_state.reactor_name = reactor_name

        st.divider()
        st.caption("厌氧反应器智能诊断系统 v0.2.0")
