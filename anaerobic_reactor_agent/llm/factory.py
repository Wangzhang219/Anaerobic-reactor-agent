"""LLM provider factory — auto-detects available providers from environment."""

import os
import logging
from typing import Optional

from .base import LLMProvider
from ..config.settings import (
    LLM_DEFAULT_MODEL,
    LLM_DEFAULT_PROVIDER,
)

logger = logging.getLogger(__name__)

# Provider detection order (first available key wins when auto-detecting)
PROVIDER_DETECTION_ORDER = [
    "deepseek",
    "zhipu",
    "claude",
    "openai",
    "gemini",
    "ollama",
]


def create_provider(provider_type: Optional[str] = None) -> Optional[LLMProvider]:
    """Create an LLM provider instance.

    Detection order:
    1. If provider_type is given, use that directly
    2. If LLM_DEFAULT_PROVIDER env var is set, use that
    3. Auto-detect: first API key found in env vars wins
    4. Otherwise return None (LLM disabled, rule-engine-only mode)

    Supported providers:
    - deepseek   (DeepSeek — https://platform.deepseek.com)
    - claude     (Anthropic Claude — https://console.anthropic.com)
    - openai     (OpenAI / any OpenAI-compatible endpoint)
    - gemini     (Google Gemini — https://aistudio.google.com)
    - zhipu      (ZhipuAI GLM 智谱 — https://open.bigmodel.cn)
    - ollama     (Local Ollama models — https://ollama.com)
    """
    provider_type = provider_type or os.getenv("ANAEROBIC_AGENT_LLM_PROVIDER", "")

    if provider_type:
        return _create_by_name(provider_type.lower())

    # Auto-detect: try each provider in order
    for name in PROVIDER_DETECTION_ORDER:
        provider = _create_by_name(name)
        if provider is not None:
            return provider

    logger.info("No LLM provider configured — running in rule-engine-only mode")
    return None


def _create_by_name(name: str) -> Optional[LLMProvider]:
    """Try to create a specific provider by name. Returns None if not configured/available."""

    if name == "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
        try:
            from .deepseek_provider import DeepSeekProvider
            provider = DeepSeekProvider(api_key=os.getenv("DEEPSEEK_API_KEY"), model="deepseek-chat")
            if provider.is_available:
                logger.info("Using DeepSeek provider: %s", provider.model_name)
                return provider
        except ImportError:
            logger.warning("openai package required for DeepSeek provider")

    elif name == "zhipu" and os.getenv("ZHIPU_API_KEY"):
        try:
            from .zhipu_provider import ZhipuProvider
            provider = ZhipuProvider(api_key=os.getenv("ZHIPU_API_KEY"), model="glm-4-flash")
            if provider.is_available:
                logger.info("Using ZhipuAI provider: %s", provider.model_name)
                return provider
        except ImportError:
            logger.warning("openai package required for ZhipuAI provider")

    elif name == "claude" and os.getenv("ANTHROPIC_API_KEY"):
        try:
            from .claude_provider import ClaudeProvider
            provider = ClaudeProvider(api_key=os.getenv("ANTHROPIC_API_KEY"), model=LLM_DEFAULT_MODEL if "claude" in LLM_DEFAULT_MODEL else "claude-sonnet-4-6")
            if provider.is_available:
                logger.info("Using Claude provider: %s", provider.model_name)
                return provider
        except ImportError:
            logger.warning("anthropic package not installed")

    elif name == "openai" and os.getenv("OPENAI_API_KEY"):
        try:
            from .openai_provider import OpenAIProvider
            model = LLM_DEFAULT_MODEL if "gpt" in LLM_DEFAULT_MODEL else "gpt-4o"
            provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"), model=model, base_url=os.getenv("OPENAI_BASE_URL"))
            if provider.is_available:
                logger.info("Using OpenAI provider: %s", provider.model_name)
                return provider
        except ImportError:
            logger.warning("openai package not installed")

    elif name == "gemini" and os.getenv("GEMINI_API_KEY"):
        try:
            from .gemini_provider import GeminiProvider
            provider = GeminiProvider(api_key=os.getenv("GEMINI_API_KEY"), model="gemini-2.5-flash")
            if provider.is_available:
                logger.info("Using Gemini provider: %s", provider.model_name)
                return provider
        except ImportError:
            logger.warning("google-generativeai package required for Gemini provider")

    elif name == "ollama":
        try:
            from .ollama_provider import OllamaProvider
            provider = OllamaProvider(base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"), model="qwen3:8b")
            if provider.is_available:
                logger.info("Using Ollama provider (local): %s", provider.model_name)
                return provider
        except ImportError:
            logger.warning("openai package required for Ollama provider")

    return None
