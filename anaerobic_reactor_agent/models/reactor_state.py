"""Reactor parameter data model."""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field


class ReactorParameters(BaseModel):
    """Input parameters describing the current state of an anaerobic reactor."""

    ph: float = Field(..., ge=0, le=14, description="pH value")
    temperature: float = Field(..., ge=0, le=100, description="Temperature in Celsius")
    cod_inlet: float = Field(..., ge=0, description="COD at inlet (mg/L)")
    cod_outlet: float = Field(..., ge=0, description="COD at outlet (mg/L)")
    vfa: float = Field(..., ge=0, description="Volatile Fatty Acids (mg/L as acetic acid)")
    alkalinity: float = Field(..., ge=0, description="Alkalinity (mg CaCO3/L)")
    orp: float = Field(..., description="Oxidation-Reduction Potential (mV)")
    biogas_production: float = Field(..., ge=0, description="Biogas production rate (m3/d)")
    methane_content: float = Field(..., ge=0, le=100, description="Methane content (%)")
    olr: float = Field(..., ge=0, description="Organic Loading Rate (kg COD/m3.d)")
    hrt: float = Field(..., ge=0, description="Hydraulic Retention Time (hours)")

    nh3_n: Optional[float] = Field(default=None, ge=0, description="Ammonia nitrogen (mg/L)")
    heavy_metals: Optional[Dict[str, float]] = Field(
        default=None, description="Heavy metal concentrations (mg/L)"
    )
    reactor_type: str = Field(default="UASB", description="Reactor type: UASB, CSTR, EGSB, IC, AnMBR")
    timestamp: datetime = Field(default_factory=datetime.now)
