"""DeepSeek LLM provider — OpenAI-compatible API."""

import logging

from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt
from ..utils.exceptions import LLMAuthError, LLMTimeoutError, LLMRateLimitError

logger = logging.getLogger(__name__)


class DeepSeekProvider(LLMProvider):
    """LLM provider using DeepSeek API (OpenAI-compatible).

    Models: deepseek-chat, deepseek-reasoner
    API docs: https://platform.deepseek.com/api-docs
    """

    BASE_URL = "https://api.deepseek.com/v1"

    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        self._api_key = api_key
        self._model = model

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

        client = openai.OpenAI(api_key=self._api_key, base_url=self.BASE_URL)

        diagnosis_json = diagnosis.model_dump_json(indent=2)

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(diagnosis_json)},
                ],
                max_tokens=4096,
                timeout=LLM_TIMEOUT_SECONDS,
            )
            return response.choices[0].message.content

        except openai.AuthenticationError as e:
            raise LLMAuthError(f"DeepSeek authentication failed: {e}") from e
        except openai.RateLimitError as e:
            raise LLMRateLimitError(f"DeepSeek rate limit exceeded: {e}") from e
        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"DeepSeek request timed out: {e}") from e
        except Exception as e:
            logger.error("DeepSeek API call failed: %s", e)
            raise
