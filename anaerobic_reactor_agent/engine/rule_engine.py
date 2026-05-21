"""Core rule engine with fuzzy logic, trend detection, and graded recommendations."""

import logging
from typing import List, Dict, Optional

from ..models.reactor_state import ReactorParameters
from ..models.rules import Condition, FaultRule, Recommendation
from ..models.diagnosis import (
    AssessmentResult,
    DiagnosedFault,
    DiagnosisResult,
    GradedRecommendation,
    ParameterStatus,
    FaultSeverity,
)
from .derived_params import compute_derived_params
from .rule_loader import RuleLoader
from .evaluator import ParameterEvaluator

logger = logging.getLogger(__name__)


class RuleEngine:
    """Fuzzy rule engine for anaerobic reactor fault diagnosis.

    Features:
    - Fuzzy evaluation near thresholds (linear transition zone)
    - Historical trend detection for time-series analysis
    - Graded recommendations (immediate / long_term / preventive)
    - Causal chain reasoning for fault explanation
    - Health score computation for radar chart visualization
    - Hot-reload support for YAML rule files
    """

    def __init__(self, loader: Optional[RuleLoader] = None):
        self.loader = loader or RuleLoader()
        self.evaluator = ParameterEvaluator(self.loader.thresholds)
        self._previous_params: Optional[dict] = None

    def diagnose(self, params: ReactorParameters, historical_data: Optional[List[dict]] = None) -> DiagnosisResult:
        """Run full diagnosis pipeline.

        Args:
            params: Current reactor parameters
            historical_data: Optional list of previous parameter dicts for trend analysis
        """
        logger.info("Starting diagnosis for reactor type=%s", params.reactor_type)

        params_dict = compute_derived_params(params)

        # Compute trends if historical data available
        trends = {}
        if historical_data and len(historical_data) >= 2:
            trends = self._compute_trends(params_dict, historical_data)
            params_dict.update(trends)
        elif self._previous_params:
            trends = self._compute_trends(params_dict, [self._previous_params])
            params_dict.update(trends)

        self._previous_params = params_dict.copy()

        assessments = self._evaluate_all_parameters(params_dict)

        faults = self._match_rules(params_dict, assessments, trends)

        recommendations = self._assemble_recommendations(faults, assessments)

        overall_status = self._determine_overall_status(assessments, faults)

        result = DiagnosisResult(
            parameter_assessments=assessments,
            overall_status=overall_status,
            faults=faults,
            recommendations=recommendations,
        )

        logger.info(
            "Diagnosis complete: status=%s, faults=%d",
            result.overall_status.value,
            len(result.faults),
        )
        return result

    def _compute_trends(self, current: dict, history: List[dict]) -> dict:
        """Compute trend indicators from historical data.

        Returns dict like {'vfa_trend': 0.05, 'ph_trend': -0.01}
        where positive = rising, negative = falling.
        """
        trends = {}
        prev = history[-1]  # most recent previous

        for key in current:
            if key.startswith("_") or key.endswith("_trend"):
                continue
            cur_val = current.get(key)
            prev_val = prev.get(key)
            if isinstance(cur_val, (int, float)) and isinstance(prev_val, (int, float)):
                if prev_val != 0:
                    trends[f"{key}_trend"] = round((cur_val - prev_val) / abs(prev_val), 3)
        return trends

    def _evaluate_all_parameters(self, params_dict: dict) -> List[AssessmentResult]:
        assessments = []
        for param_name, value in params_dict.items():
            if isinstance(value, (int, float)) and not param_name.startswith("_"):
                if param_name.endswith("_trend"):
                    continue
                result = self.evaluator.evaluate(param_name, value)
                if result is not None:
                    # Compute health score (1 - severity)
                    result.health_score = round(1.0 - result.severity_score, 2)
                    assessments.append(result)
        return assessments

    def _match_rules(self, params_dict: dict, assessments: List[AssessmentResult], trends: dict) -> List[DiagnosedFault]:
        triggered_faults: Dict[str, DiagnosedFault] = {}

        for rule in self.loader.rules:
            confidence = self._evaluate_rule(rule, params_dict)

            if confidence >= rule.min_confidence:
                logger.debug("Rule '%s' triggered (confidence: %.2f)", rule.name, confidence)

                if rule.fault_type in triggered_faults:
                    existing = triggered_faults[rule.fault_type]
                    existing.confidence = max(existing.confidence, confidence)
                    existing.matched_rules.append(rule.name)
                    existing.evidence.extend(self._collect_evidence(rule, assessments))
                    for r in rule.recommendations:
                        existing.recommendations.append(
                            GradedRecommendation(text=r.text, level=r.level)
                        )
                    if self._severity_rank(rule.severity) > self._severity_rank(existing.severity.value):
                        existing.severity = FaultSeverity(rule.severity)
                        existing.causal_chain = rule.causal_chain
                else:
                    triggered_faults[rule.fault_type] = DiagnosedFault(
                        fault_type=rule.fault_type,
                        confidence=confidence,
                        matched_rules=[rule.name],
                        evidence=self._collect_evidence(rule, assessments),
                        severity=FaultSeverity(rule.severity),
                        description=rule.description,
                        causal_chain=rule.causal_chain,
                        recommendations=[
                            GradedRecommendation(text=r.text, level=r.level)
                            for r in rule.recommendations
                        ],
                    )

        faults = list(triggered_faults.values())
        for f in faults:
            # Deduplicate recommendations by text
            seen = set()
            unique_recs = []
            for r in f.recommendations:
                if r.text not in seen:
                    seen.add(r.text)
                    unique_recs.append(r)
            f.recommendations = unique_recs
            f.evidence = list(dict.fromkeys(f.evidence))

        return sorted(faults, key=lambda f: -f.confidence)

    def _evaluate_rule(self, rule: FaultRule, params_dict: dict) -> float:
        total_weight = sum(c.weight for c in rule.conditions)
        if total_weight == 0:
            return 0.0

        weighted_score = 0.0
        for condition in rule.conditions:
            actual = params_dict.get(condition.parameter)
            if actual is None:
                continue
            satisfied = self._check_condition_fuzzy(actual, condition)
            weighted_score += satisfied * condition.weight

        return round(weighted_score / total_weight, 3)

    def _check_condition_fuzzy(self, actual: float, condition: Condition) -> float:
        """Evaluate a condition with optional fuzzy logic.

        Non-fuzzy: returns 0.0 or 1.0 (classic binary)
        Fuzzy: returns 0.0 to 1.0 with linear transition zone around threshold
        """
        op = condition.operator
        threshold = condition.value
        fuzzy = condition.fuzzy

        if fuzzy:
            return self._fuzzy_evaluate(actual, op, threshold)
        else:
            return self._crisp_evaluate(actual, op, threshold)

    def _crisp_evaluate(self, actual: float, op: str, threshold) -> float:
        """Binary condition evaluation. Returns 0.0 or 1.0."""
        if op == ">":
            return 1.0 if actual > threshold else 0.0
        elif op == "<":
            return 1.0 if actual < threshold else 0.0
        elif op == ">=":
            return 1.0 if actual >= threshold else 0.0
        elif op == "<=":
            return 1.0 if actual <= threshold else 0.0
        elif op == "==":
            return 1.0 if actual == threshold else 0.0
        elif op == "!=":
            return 1.0 if actual != threshold else 0.0
        elif op == "between":
            low, high = threshold[0], threshold[1]
            return 1.0 if low <= actual <= high else 0.0
        elif op == "not_between":
            low, high = threshold[0], threshold[1]
            return 1.0 if actual < low or actual > high else 0.0
        elif op == "trend":
            # trend: actual is the rate of change (e.g. 0.05 = 5% increase per period)
            if isinstance(threshold, list):
                low, high = threshold[0], threshold[1]
                return 1.0 if low <= actual <= high else 0.0
            return 1.0 if abs(actual) > abs(threshold) else 0.0
        else:
            logger.warning("Unknown operator '%s'", op)
            return 0.0

    def _fuzzy_evaluate(self, actual: float, op: str, threshold) -> float:
        """Fuzzy condition evaluation with linear transition zone.

        For '>' operator: actual near threshold produces smooth 0→1 transition.
        Transition zone is ±20% of threshold value.
        """
        transition = abs(threshold) * 0.2 if isinstance(threshold, (int, float)) and threshold != 0 else 0.1

        if op == ">":
            if actual > threshold:
                return 1.0
            elif actual >= threshold - transition:
                return (actual - (threshold - transition)) / transition
            return 0.0

        elif op == "<":
            if actual < threshold:
                return 1.0
            elif actual <= threshold + transition:
                return 1.0 - (actual - threshold) / transition
            return 0.0

        elif op == ">=":
            if actual >= threshold:
                return 1.0
            elif actual >= threshold - transition:
                return (actual - (threshold - transition)) / transition
            return 0.0

        elif op == "<=":
            if actual <= threshold:
                return 1.0
            elif actual <= threshold + transition:
                return 1.0 - (actual - threshold) / transition
            return 0.0

        else:
            return self._crisp_evaluate(actual, op, threshold)

    def _collect_evidence(self, rule: FaultRule, assessments: List[AssessmentResult]) -> List[str]:
        evidence = []
        for cond in rule.conditions:
            for a in assessments:
                if a.parameter_name == cond.parameter and a.status != ParameterStatus.NORMAL:
                    evidence.append(a.message)
        return evidence

    def _assemble_recommendations(
        self, faults: List[DiagnosedFault], assessments: List[AssessmentResult]
    ) -> List[GradedRecommendation]:
        recs: List[GradedRecommendation] = []

        # Priority-ordered: immediate first, then long_term, then preventive
        for fault in faults:
            for r in fault.recommendations:
                recs.append(r)

        # Add fault-specific knowledge base recommendations
        fault_specific = self.loader.recommendations.get("fault_specific", {})
        for fault in faults:
            kb = fault_specific.get(fault.fault_type, {})
            for level_key in ("immediate", "long_term", "preventive"):
                for r in kb.get(level_key, []):
                    if isinstance(r, dict):
                        recs.append(GradedRecommendation(
                            text=r.get("text", ""),
                            level=r.get("level", level_key),
                        ))

        # General recommendations based on overall status
        status = self._determine_overall_status(assessments, faults)
        general = self.loader.recommendations.get("general", {})
        status_recs = general.get(status.value, [])
        for r in status_recs:
            if isinstance(r, dict):
                recs.append(GradedRecommendation(text=r.get("text", ""), level=r.get("level", "long_term")))
            elif isinstance(r, str):
                recs.append(GradedRecommendation(text=r, level="long_term"))

        # Deduplicate and sort: immediate > long_term > preventive
        seen = set()
        unique = []
        for r in recs:
            if r.text not in seen:
                seen.add(r.text)
                unique.append(r)

        level_order = {"immediate": 0, "long_term": 1, "preventive": 2}
        unique.sort(key=lambda r: level_order.get(r.level, 5))

        return unique

    def _determine_overall_status(
        self, assessments: List[AssessmentResult], faults: List[DiagnosedFault]
    ) -> ParameterStatus:
        has_alarm = any(a.status == ParameterStatus.ALARM for a in assessments)
        has_warning = any(a.status == ParameterStatus.WARNING for a in assessments)
        has_fault = len(faults) > 0

        if has_alarm or any(f.severity in (FaultSeverity.ALARM, FaultSeverity.CRITICAL) for f in faults):
            return ParameterStatus.ALARM
        elif has_warning or has_fault:
            return ParameterStatus.WARNING
        return ParameterStatus.NORMAL

    def _severity_rank(self, severity: str) -> int:
        ranks = {"warning": 1, "alarm": 2, "critical": 3}
        return ranks.get(severity, 0)

    def reload_rules(self):
        """Hot-reload YAML rule files without restarting."""
        self.loader.reload()
        self.evaluator = ParameterEvaluator(self.loader.thresholds)
        logger.info("Rules hot-reloaded")
