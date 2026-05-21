"""Custom exception hierarchy for the anaerobic reactor agent."""


class AnaerobicAgentError(Exception):
    """Base exception for all agent errors."""
    pass


class ConfigurationError(AnaerobicAgentError):
    """Raised when configuration is missing or invalid."""
    pass


class ValidationError(AnaerobicAgentError):
    """Raised when input parameters fail validation."""
    pass


class RuleEvaluationError(AnaerobicAgentError):
    """Raised when the rule engine encounters an error during evaluation."""
    pass


class LLMError(AnaerobicAgentError):
    """Base exception for LLM provider failures."""
    pass


class LLMAuthError(LLMError):
    """Raised when LLM authentication fails."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when an LLM request times out."""
    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limits are exceeded."""
    pass
