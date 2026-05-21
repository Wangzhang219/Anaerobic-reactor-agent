"""Anthropic Claude LLM provider implementation."""

import logging

from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt
from ..utils.exceptions import LLMAuthError, LLMTimeoutError, LLMRateLimitError

logger = logging.getLogger(__name__)


class ClaudeProvider(LLMProvider):
    """LLM provider using Anthropic's Claude API."""

    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-6"):
        self._api_key = api_key
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def is_available(self) -> bool:
        try:
            import anthropic
            return True
        except ImportError:
            return False

    def analyze(self, diagnosis) -> str:
        import anthropic
        from ..config.settings import LLM_TIMEOUT_SECONDS

        client = anthropic.Anthropic(api_key=self._api_key)

        diagnosis_json = diagnosis.model_dump_json(indent=2)

        try:
            response = client.messages.create(
                model=self._model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": build_user_prompt(diagnosis_json)},
                ],
                timeout=LLM_TIMEOUT_SECONDS,
            )
            return response.content[0].text

        except anthropic.AuthenticationError as e:
            raise LLMAuthError(f"Claude authentication failed: {e}") from e
        except anthropic.RateLimitError as e:
            raise LLMRateLimitError(f"Claude rate limit exceeded: {e}") from e
        except anthropic.APITimeoutError as e:
            raise LLMTimeoutError(f"Claude request timed out: {e}") from e
        except Exception as e:
            logger.error("Claude API call failed: %s", e)
            raise
