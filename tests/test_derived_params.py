"""Tests for derived parameter computation."""

from datetime import datetime

from anaerobic_reactor_agent.models.reactor_state import ReactorParameters
from anaerobic_reactor_agent.engine.derived_params import compute_derived_params


class TestComputeDerivedParams:
    def test_cod_removal_rate(self):
        p = ReactorParameters(
            ph=7.0, temperature=35, cod_inlet=5000, cod_outlet=500,
            vfa=150, alkalinity=2000, orp=-350, biogas_production=50,
            methane_content=65, olr=5, hrt=12,
        )
        result = compute_derived_params(p)
        assert result["cod_removal_rate"] == 90.0

    def test_cod_removal_rate_zero_inlet(self):
        p = ReactorParameters(
            ph=7.0, temperature=35, cod_inlet=0, cod_outlet=0,
            vfa=150, alkalinity=2000, orp=-350, biogas_production=50,
            methane_content=65, olr=5, hrt=12,
        )
        result = compute_derived_params(p)
        assert "cod_removal_rate" not in result

    def test_vfa_alkalinity_ratio(self):
        p = ReactorParameters(
            ph=7.0, temperature=35, cod_inlet=5000, cod_outlet=500,
            vfa=400, alkalinity=2000, orp=-350, biogas_production=50,
            methane_content=65, olr=5, hrt=12,
        )
        result = compute_derived_params(p)
        assert result["vfa_alkalinity_ratio"] == 0.2

    def test_ratio_zero_alkalinity(self):
        p = ReactorParameters(
            ph=7.0, temperature=35, cod_inlet=5000, cod_outlet=500,
            vfa=150, alkalinity=0, orp=-350, biogas_production=50,
            methane_content=65, olr=5, hrt=12,
        )
        result = compute_derived_params(p)
        assert "vfa_alkalinity_ratio" not in result

    def test_raw_params_preserved(self):
        p = ReactorParameters(
            ph=7.0, temperature=35, cod_inlet=5000, cod_outlet=500,
            vfa=150, alkalinity=2000, orp=-350, biogas_production=50,
            methane_content=65, olr=5, hrt=12,
        )
        result = compute_derived_params(p)
        assert result["ph"] == 7.0
        assert result["temperature"] == 35.0
