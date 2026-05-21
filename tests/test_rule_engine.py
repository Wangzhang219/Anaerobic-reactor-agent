"""Integration tests for the rule engine — full diagnosis pipeline."""

import pytest

from anaerobic_reactor_agent.models.diagnosis import ParameterStatus


class TestRuleEngineDiagnosis:

    def test_normal_params_no_faults(self, rule_engine, normal_params):
        result = rule_engine.diagnose(normal_params)
        assert result.overall_status == ParameterStatus.NORMAL
        assert len(result.faults) == 0

    def test_acidification_detected(self, rule_engine, acidification_params):
        result = rule_engine.diagnose(acidification_params)
        fault_types = [f.fault_type for f in result.faults]
        assert "acidification" in fault_types
        assert result.overall_status == ParameterStatus.ALARM

    def test_ammonia_inhibition_detected(self, rule_engine, ammonia_inhibition_params):
        result = rule_engine.diagnose(ammonia_inhibition_params)
        fault_types = [f.fault_type for f in result.faults]
        assert "ammonia_inhibition" in fault_types

    def test_temperature_shock_detected(self, rule_engine, temperature_shock_params):
        result = rule_engine.diagnose(temperature_shock_params)
        fault_types = [f.fault_type for f in result.faults]
        assert "temperature_shock" in fault_types

    def test_organic_overload_detected(self, rule_engine, organic_overload_params):
        result = rule_engine.diagnose(organic_overload_params)
        fault_types = [f.fault_type for f in result.faults]
        assert "organic_overload" in fault_types

    def test_sludge_washout_detected(self, rule_engine, sludge_washout_params):
        result = rule_engine.diagnose(sludge_washout_params)
        fault_types = [f.fault_type for f in result.faults]
        assert "sludge_washout" in fault_types

    def test_toxic_inhibition_detected(self, rule_engine, toxic_inhibition_params):
        result = rule_engine.diagnose(toxic_inhibition_params)
        fault_types = [f.fault_type for f in result.faults]
        assert "toxic_inhibition" in fault_types

    def test_multi_fault_detection(self, rule_engine, multi_fault_params):
        result = rule_engine.diagnose(multi_fault_params)
        fault_types = [f.fault_type for f in result.faults]
        assert "acidification" in fault_types
        assert "organic_overload" in fault_types
        assert len(result.faults) >= 2

    def test_diagnosis_has_recommendations(self, rule_engine, acidification_params):
        result = rule_engine.diagnose(acidification_params)
        assert len(result.recommendations) > 0

    def test_diagnosis_has_assessments(self, rule_engine, normal_params):
        result = rule_engine.diagnose(normal_params)
        param_names = [a.parameter_name for a in result.parameter_assessments]
        assert "ph" in param_names
        assert "vfa" in param_names

    def test_normal_has_no_llm_analysis(self, rule_engine, normal_params):
        result = rule_engine.diagnose(normal_params)
        assert result.llm_analysis is None

    def test_acidification_confidence_above_threshold(self, rule_engine, acidification_params):
        result = rule_engine.diagnose(acidification_params)
        acid_fault = next(f for f in result.faults if f.fault_type == "acidification")
        assert acid_fault.confidence >= 0.5

    def test_fault_recommendations_are_deduplicated(self, rule_engine, multi_fault_params):
        result = rule_engine.diagnose(multi_fault_params)
        texts = [r.text for r in result.recommendations]
        assert len(texts) == len(set(texts))
