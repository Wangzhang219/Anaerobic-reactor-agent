"""Unit tests for data models."""

import pytest
from datetime import datetime

from anaerobic_reactor_agent.models.reactor_state import ReactorParameters
from anaerobic_reactor_agent.models.rules import Condition, FaultRule
from anaerobic_reactor_agent.models.diagnosis import (
    AssessmentResult,
    DiagnosedFault,
    DiagnosisResult,
    ParameterStatus,
    FaultSeverity,
)


class TestReactorParameters:
    def test_valid_params(self):
        p = ReactorParameters(
            ph=7.0, temperature=35, cod_inlet=5000, cod_outlet=500,
            vfa=150, alkalinity=2000, orp=-350, biogas_production=50,
            methane_content=65, olr=5, hrt=12,
        )
        assert p.ph == 7.0
        assert p.reactor_type == "UASB"
        assert isinstance(p.timestamp, datetime)

    def test_optional_fields_default(self):
        p = ReactorParameters(
            ph=7.0, temperature=35, cod_inlet=5000, cod_outlet=500,
            vfa=150, alkalinity=2000, orp=-350, biogas_production=50,
            methane_content=65, olr=5, hrt=12,
        )
        assert p.nh3_n is None
        assert p.heavy_metals is None

    def test_optional_fields_set(self):
        p = ReactorParameters(
            ph=7.0, temperature=35, cod_inlet=5000, cod_outlet=500,
            vfa=150, alkalinity=2000, orp=-350, biogas_production=50,
            methane_content=65, olr=5, hrt=12,
            nh3_n=100, heavy_metals={"Cu": 0.5, "Zn": 1.0},
        )
        assert p.nh3_n == 100
        assert p.heavy_metals == {"Cu": 0.5, "Zn": 1.0}

    def test_ph_out_of_range_raises_error(self):
        with pytest.raises(Exception):
            ReactorParameters(
                ph=15.0, temperature=35, cod_inlet=5000, cod_outlet=500,
                vfa=150, alkalinity=2000, orp=-350, biogas_production=50,
                methane_content=65, olr=5, hrt=12,
            )

    def test_negative_cod_raises_error(self):
        with pytest.raises(Exception):
            ReactorParameters(
                ph=7.0, temperature=35, cod_inlet=-100, cod_outlet=500,
                vfa=150, alkalinity=2000, orp=-350, biogas_production=50,
                methane_content=65, olr=5, hrt=12,
            )


class TestDiagnosisResult:
    def test_healthy_result(self):
        result = DiagnosisResult(overall_status=ParameterStatus.NORMAL)
        assert result.is_healthy is True
        assert result.fault_count == 0

    def test_faulty_result(self):
        fault = DiagnosedFault(
            fault_type="acidification", confidence=0.8,
            severity=FaultSeverity.ALARM,
        )
        result = DiagnosisResult(
            overall_status=ParameterStatus.ALARM,
            faults=[fault],
        )
        assert result.is_healthy is False
        assert result.fault_count == 1
