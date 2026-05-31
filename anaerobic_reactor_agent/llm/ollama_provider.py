"""Ollama local LLM provider — OpenAI-compatible API."""

import logging

from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt, build_compact_summary
from ..utils.exceptions import LLMAuthError, LLMTimeoutError, LLMRateLimitError

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """LLM provider using local Ollama models (OpenAI-compatible).

    Prerequisites: Install Ollama from https://ollama.com
    Recommended models: llama3.2, qwen3, mistral, deepseek-r1:8b

    Usage:
        ollama pull qwen3:8b
        ollama serve
    """

    BASE_URL = "http://localhost:11434/v1"

    def __init__(self, api_key: str = "ollama", model: str = "qwen3:8b", base_url: str = None):
        self._api_key = api_key  # Ollama doesn't need a real key
        self._model = model
        self._base_url = base_url or self.BASE_URL

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def is_available(self) -> bool:
        try:
            import openai
            return True
        except ImportError:
            return False

    def analyze(self, diagnosis) -> str:
        import openai
        from ..config.settings import LLM_TIMEOUT_SECONDS

        client = openai.OpenAI(api_key=self._api_key, base_url=self._base_url)

        summary = build_compact_summary(diagnosis)

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(summary)},
                ],
                max_tokens=2048,
                timeout=LLM_TIMEOUT_SECONDS,
            )
            return response.choices[0].message.content

        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"Ollama request timed out (model '{self._model}' may be loading): {e}") from e
        except Exception as e:
            error_str = str(e).lower()
            if "connection" in error_str or "refused" in error_str:
                raise LLMAuthError(
                    f"Cannot connect to Ollama at {self._base_url}. "
                    f"Is Ollama running? Run 'ollama serve' first."
                ) from e
            logger.error("Ollama API call failed: %s", e)
            raise
