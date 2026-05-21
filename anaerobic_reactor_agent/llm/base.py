"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract interface for LLM backends."""

    @abstractmethod
    def analyze(self, diagnosis) -> str:
        """Send diagnosis to LLM and return natural language analysis."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        ...

    @property
    def is_available(self) -> bool:
        """Check if the provider is configured and accessible."""
        return True
