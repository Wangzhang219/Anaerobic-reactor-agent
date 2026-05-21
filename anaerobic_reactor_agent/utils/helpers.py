"""Utility helper functions."""


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a value to [lo, hi] range."""
    return max(lo, min(hi, value))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide with fallback if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
