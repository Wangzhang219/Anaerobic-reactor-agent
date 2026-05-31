"""ZhipuAI (智谱 GLM) LLM provider — OpenAI-compatible API."""

import logging

from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt, build_compact_summary
from ..utils.exceptions import LLMAuthError, LLMTimeoutError, LLMRateLimitError

logger = logging.getLogger(__name__)


class ZhipuProvider(LLMProvider):
    """LLM provider using ZhipuAI (智谱 AI) API (OpenAI-compatible).

    Models: glm-4-flash, glm-4, glm-4-plus, glm-4-long
    API docs: https://open.bigmodel.cn/dev/api
    """

    BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

    def __init__(self, api_key: str = None, model: str = "glm-4-flash"):
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

        summary = build_compact_summary(diagnosis)

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(summary)},
                ],
                max_tokens=4096,
                timeout=LLM_TIMEOUT_SECONDS,
            )
            return response.choices[0].message.content

        except openai.AuthenticationError as e:
            raise LLMAuthError(f"ZhipuAI authentication failed: {e}") from e
        except openai.RateLimitError as e:
            raise LLMRateLimitError(f"ZhipuAI rate limit exceeded: {e}") from e
        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"ZhipuAI request timed out: {e}") from e
        except Exception as e:
            logger.error("ZhipuAI API call failed: %s", e)
            raise
