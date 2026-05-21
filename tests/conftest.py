"""Shared pytest fixtures for anaerobic reactor testing."""

import pytest
from datetime import datetime

from anaerobic_reactor_agent.models.reactor_state import ReactorParameters
from anaerobic_reactor_agent.engine.rule_engine import RuleEngine
from anaerobic_reactor_agent.engine.rule_loader import RuleLoader


@pytest.fixture
def rule_engine():
    """Return a fully initialized RuleEngine with default YAML rules."""
    return RuleEngine()


@pytest.fixture
def normal_params():
    """Normal operating conditions — no faults expected."""
    return ReactorParameters(
        ph=7.0,
        temperature=35.0,
        cod_inlet=5000.0,
        cod_outlet=500.0,
        vfa=150.0,
        alkalinity=2000.0,
        orp=-350.0,
        biogas_production=50.0,
        methane_content=65.0,
        olr=5.0,
        hrt=12.0,
        nh3_n=50.0,
        reactor_type="UASB",
        timestamp=datetime.now(),
    )


@pytest.fixture
def acidification_params():
    """Classic acidification: VFA high, pH low, VFA/ALK ratio elevated."""
    return ReactorParameters(
        ph=6.2,
        temperature=35.0,
        cod_inlet=5000.0,
        cod_outlet=2500.0,
        vfa=800.0,
        alkalinity=1500.0,
        orp=-250.0,
        biogas_production=30.0,
        methane_content=55.0,
        olr=8.0,
        hrt=12.0,
        nh3_n=50.0,
        reactor_type="UASB",
        timestamp=datetime.now(),
    )


@pytest.fixture
def ammonia_inhibition_params():
    """Ammonia inhibition: high NH3-N, low methane."""
    return ReactorParameters(
        ph=7.9,
        temperature=38.0,
        cod_inlet=4000.0,
        cod_outlet=600.0,
        vfa=200.0,
        alkalinity=2500.0,
        orp=-350.0,
        biogas_production=40.0,
        methane_content=45.0,
        olr=5.0,
        hrt=12.0,
        nh3_n=200.0,
        reactor_type="CSTR",
        timestamp=datetime.now(),
    )


@pytest.fixture
def temperature_shock_params():
    """Temperature shock: cold temperature, low biogas and COD removal."""
    return ReactorParameters(
        ph=7.0,
        temperature=25.0,
        cod_inlet=5000.0,
        cod_outlet=2000.0,
        vfa=200.0,
        alkalinity=2000.0,
        orp=-350.0,
        biogas_production=8.0,
        methane_content=55.0,
        olr=5.0,
        hrt=12.0,
        nh3_n=50.0,
        reactor_type="UASB",
        timestamp=datetime.now(),
    )


@pytest.fixture
def organic_overload_params():
    """Organic overload: high OLR, reduced COD removal, elevated VFA."""
    return ReactorParameters(
        ph=6.9,
        temperature=35.0,
        cod_inlet=8000.0,
        cod_outlet=3200.0,
        vfa=450.0,
        alkalinity=2000.0,
        orp=-300.0,
        biogas_production=60.0,
        methane_content=60.0,
        olr=12.0,
        hrt=10.0,
        nh3_n=50.0,
        reactor_type="UASB",
        timestamp=datetime.now(),
    )


@pytest.fixture
def sludge_washout_params():
    """Sludge washout: very short HRT, poor COD removal."""
    return ReactorParameters(
        ph=7.0,
        temperature=35.0,
        cod_inlet=5000.0,
        cod_outlet=2500.0,
        vfa=200.0,
        alkalinity=2000.0,
        orp=-350.0,
        biogas_production=40.0,
        methane_content=60.0,
        olr=5.0,
        hrt=4.0,
        nh3_n=50.0,
        reactor_type="UASB",
        timestamp=datetime.now(),
    )


@pytest.fixture
def toxic_inhibition_params():
    """Toxic inhibition: very low biogas and methane, low pH."""
    return ReactorParameters(
        ph=5.8,
        temperature=35.0,
        cod_inlet=5000.0,
        cod_outlet=4000.0,
        vfa=600.0,
        alkalinity=1000.0,
        orp=-100.0,
        biogas_production=3.0,
        methane_content=40.0,
        olr=5.0,
        hrt=12.0,
        nh3_n=30.0,
        reactor_type="UASB",
        timestamp=datetime.now(),
    )


@pytest.fixture
def multi_fault_params():
    """Multiple faults: acidification + organic overload."""
    return ReactorParameters(
        ph=6.3,
        temperature=35.0,
        cod_inlet=8000.0,
        cod_outlet=4800.0,
        vfa=700.0,
        alkalinity=1200.0,
        orp=-250.0,
        biogas_production=25.0,
        methane_content=50.0,
        olr=14.0,
        hrt=8.0,
        nh3_n=50.0,
        reactor_type="UASB",
        timestamp=datetime.now(),
    )
