"""Parameter threshold evaluation — compare values against normal/warning/alarm ranges."""

import logging
from typing import Optional

from ..models.diagnosis import AssessmentResult, ParameterStatus
from ..utils.helpers import clamp

logger = logging.getLogger(__name__)


class ParameterEvaluator:
    """Evaluates individual parameters against configured thresholds."""

    def __init__(self, thresholds: dict):
        self.thresholds = thresholds

    def evaluate(self, param_name: str, value: float) -> Optional[AssessmentResult]:
        """Evaluate a single parameter and return an AssessmentResult, or None if no threshold config."""
        th = self.thresholds.get("parameters", {}).get(param_name)
        if th is None:
            return None

        unit = th.get("unit", "")
        status, message, severity = self._classify(param_name, value, th)
        normal_range = self._format_normal_range(th)

        return AssessmentResult(
            parameter_name=param_name,
            current_value=value,
            status=status,
            severity_score=severity,
            normal_range=normal_range,
            message=message,
        )

    def _classify(self, name: str, value: float, th: dict) -> tuple:
        """Determine status, generate message, compute severity for a value."""
        # Check for low-range alarm/warning/normal patterns
        if "alarm_low" in th or "warning_low" in th:
            return self._classify_low_high(name, value, th)

        # Check for range-based alarm/warning/normal
        if "alarm_range" in th or "warning_range" in th:
            return self._classify_ranged(name, value, th)

        # Fallback: use only normal range
        normal = th.get("normal", [])
        if len(normal) >= 2 and normal[0] <= value <= normal[1]:
            return ParameterStatus.NORMAL, f"{name}={value} {th.get('unit','')}, within normal range", 0.0
        else:
            return ParameterStatus.WARNING, f"{name}={value} {th.get('unit','')}, outside normal range", 0.5

    def _classify_low_high(self, name: str, value: float, th: dict) -> tuple:
        """Handle thresholds with separate low/high alarm and warning ranges (e.g., pH, temperature)."""
        normal = th.get("normal", [0, 0])
        unit = th.get("unit", "")

        # Check alarm_low
        alarm_low = th.get("alarm_low")
        if alarm_low and len(alarm_low) >= 2 and alarm_low[0] <= value <= alarm_low[1]:
            severity = self._interpolate_severity(value, alarm_low, too_low=True)
            return ParameterStatus.ALARM, f"{name}={value}{unit}, critically low", severity

        # Check alarm_high
        alarm_high = th.get("alarm_high")
        if alarm_high and len(alarm_high) >= 2 and alarm_high[0] <= value <= alarm_high[1]:
            severity = self._interpolate_severity(value, alarm_high, too_low=False)
            return ParameterStatus.ALARM, f"{name}={value}{unit}, critically high", severity

        # Check warning_low
        warning_low = th.get("warning_low")
        if warning_low and len(warning_low) >= 2 and warning_low[0] <= value <= warning_low[1]:
            severity = self._interpolate_severity(value, warning_low, too_low=True)
            return ParameterStatus.WARNING, f"{name}={value}{unit}, below optimal range", severity

        # Check warning_high
        warning_high = th.get("warning_high")
        if warning_high and len(warning_high) >= 2 and warning_high[0] <= value <= warning_high[1]:
            severity = self._interpolate_severity(value, warning_high, too_low=False)
            return ParameterStatus.WARNING, f"{name}={value}{unit}, above optimal range", severity

        # Normal
        return ParameterStatus.NORMAL, f"{name}={value}{unit}, within normal range", 0.0

    def _classify_ranged(self, name: str, value: float, th: dict) -> tuple:
        """Handle thresholds with alarm_range/warning_range patterns."""
        normal = th.get("normal", [0, 0])
        unit = th.get("unit", "")

        # Check alarm_range
        alarm_range = th.get("alarm_range")
        if alarm_range and len(alarm_range) >= 2 and alarm_range[0] <= value <= alarm_range[1]:
            severity = self._interpolate_severity(value, alarm_range, too_low=True)
            return ParameterStatus.ALARM, f"{name}={value}{unit}, in alarm range", severity

        # Check warning_range
        warning_range = th.get("warning_range")
        if warning_range and len(warning_range) >= 2 and warning_range[0] <= value <= warning_range[1]:
            severity = self._interpolate_severity(value, warning_range, too_low=True)
            return ParameterStatus.WARNING, f"{name}={value}{unit}, in warning range", severity

        # Normal
        if len(normal) >= 2 and normal[0] <= value <= normal[1]:
            return ParameterStatus.NORMAL, f"{name}={value}{unit}, within normal range", 0.0

        # Outside all defined ranges
        return ParameterStatus.WARNING, f"{name}={value}{unit}, outside tracked range", 0.5

    def _interpolate_severity(self, value: float, rng: list, too_low: bool) -> float:
        """Linear interpolate severity within a range. Returns 0.0-1.0."""
        if len(rng) < 2:
            return 0.5

        lo, hi = rng[0], rng[1]
        if hi == lo:
            return 1.0

        if too_low:
            # Closer to lo = more severe
            ratio = (value - lo) / (hi - lo)
            severity = 1.0 - ratio
        else:
            # Closer to hi = more severe
            ratio = (value - lo) / (hi - lo)
            severity = ratio

        return round(clamp(severity, 0.0, 1.0), 2)

    def _format_normal_range(self, th: dict) -> str:
        normal = th.get("normal", [])
        if len(normal) >= 2:
            return f"{normal[0]} - {normal[1]}"
        return "N/A"
