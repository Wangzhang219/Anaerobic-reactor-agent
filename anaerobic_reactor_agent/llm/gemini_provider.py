"""Google Gemini LLM provider."""

import logging

from .base import LLMProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt
from ..utils.exceptions import LLMAuthError, LLMTimeoutError, LLMRateLimitError

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """LLM provider using Google's Gemini API.

    Models: gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash
    API docs: https://ai.google.dev/gemini-api/docs
    """

    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        self._api_key = api_key
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def is_available(self) -> bool:
        try:
            import google.generativeai
            return True
        except ImportError:
            return False

    def analyze(self, diagnosis) -> str:
        import google.generativeai as genai
        from ..config.settings import LLM_TIMEOUT_SECONDS

        genai.configure(api_key=self._api_key)

        diagnosis_json = diagnosis.model_dump_json(indent=2)
        prompt = f"""{SYSTEM_PROMPT}

---

{build_user_prompt(diagnosis_json)}"""

        try:
            model = genai.GenerativeModel(self._model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2048,
                ),
                request_options={"timeout": LLM_TIMEOUT_SECONDS * 1000},
            )
            return response.text

        except genai.errors.AuthenticationError as e:
            raise LLMAuthError(f"Gemini authentication failed: {e}") from e
        except genai.errors.ResourceExhaustedError as e:
            raise LLMRateLimitError(f"Gemini rate limit exceeded: {e}") from e
        except Exception as e:
            error_str = str(e).lower()
            if "timeout" in error_str or "deadline" in error_str:
                raise LLMTimeoutError(f"Gemini request timed out: {e}") from e
            logger.error("Gemini API call failed: %s", e)
            raise
