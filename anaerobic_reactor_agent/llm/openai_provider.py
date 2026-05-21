"""OpenAI-compatible LLM provider implementation."""

import logging

from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt
from ..utils.exceptions import LLMAuthError, LLMTimeoutError, LLMRateLimitError

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """LLM provider using OpenAI or OpenAI-compatible API."""

    def __init__(self, api_key: str = None, model: str = "gpt-4o", base_url: str = None):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url

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

        client_kwargs = {"api_key": self._api_key}
        if self._base_url:
            client_kwargs["base_url"] = self._base_url

        client = openai.OpenAI(**client_kwargs)

        diagnosis_json = diagnosis.model_dump_json(indent=2)

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(diagnosis_json)},
                ],
                max_tokens=2048,
                timeout=LLM_TIMEOUT_SECONDS,
            )
            return response.choices[0].message.content

        except openai.AuthenticationError as e:
            raise LLMAuthError(f"OpenAI authentication failed: {e}") from e
        except openai.RateLimitError as e:
            raise LLMRateLimitError(f"OpenAI rate limit exceeded: {e}") from e
        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"OpenAI request timed out: {e}") from e
        except Exception as e:
            logger.error("OpenAI API call failed: %s", e)
            raise
