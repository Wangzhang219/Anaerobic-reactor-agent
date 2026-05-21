# -*- coding: utf-8 -*-
"""
Anaerobic Reactor Intelligent Agent - Demo Script
Run: python demo.py
"""
import sys
import io
# Fix Windows console encoding for Chinese characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from anaerobic_reactor_agent.engine.rule_engine import RuleEngine
from anaerobic_reactor_agent.models.reactor_state import ReactorParameters

# ============================================================
# Modify your reactor parameters here
# ============================================================
params = ReactorParameters(
    ph=6.2,                # pH (normal 6.8-7.5)
    temperature=35,        # Temperature C (normal 30-40)
    cod_inlet=5000,        # COD Inlet mg/L
    cod_outlet=2500,       # COD Outlet mg/L (removal rate only 50%!)
    vfa=800,               # VFA mg/L (normal <300)
    alkalinity=1500,       # Alkalinity mg CaCO3/L (normal 1000-5000)
    orp=-250,              # ORP mV (normal < -300)
    biogas_production=30,  # Biogas production m3/d
    methane_content=55,    # Methane content % (normal 55-70)
    olr=8,                 # OLR kg COD/m3.d (normal 2-10)
    hrt=12,                # HRT hours (normal 6-48)
    nh3_n=50,              # NH3-N mg/L (optional, >150 inhibitory)
)

# ============================================================
# Run diagnosis
# ============================================================
engine = RuleEngine()
result = engine.diagnose(params)

# ============================================================
# Results
# ============================================================
print("=" * 60)
print(f"Overall Status: {result.overall_status.value.upper()}")
print(f"Faults Detected: {result.fault_count}")
print("=" * 60)

if result.faults:
    for fault in result.faults:
        print(f"\n[{fault.severity.value.upper()}] {fault.fault_type}")
        print(f"  Confidence: {fault.confidence:.0%}")
        print(f"  Description: {fault.description}")
        print(f"  Evidence:")
        for e in fault.evidence:
            print(f"    - {e}")
        print(f"  Recommendations:")
        for rec in fault.recommendations:
            print(f"    - [{rec.level}] {rec.text}")
else:
    print("\nReactor operating normally. No faults detected.")

# ============================================================
# Per-parameter assessment
# ============================================================
print("\n" + "=" * 60)
print("Parameter Assessment")
print("=" * 60)
for a in result.parameter_assessments:
    status_icon = {"normal": "[OK]", "warning": "[!!]", "alarm": "[XXX]"}.get(a.status.value, "[?]")
    print(f"{status_icon} {a.parameter_name}: {a.current_value} ({a.status.value}) - {a.message}")

print("\n" + "=" * 60)
print("Recommendations Summary")
print("=" * 60)
for i, rec in enumerate(result.recommendations, 1):
    print(f"  {i}. [{rec.level}] {rec.text}")
