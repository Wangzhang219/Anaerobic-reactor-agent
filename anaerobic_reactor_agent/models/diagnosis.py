"""Diagnosis result models."""

from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ParameterStatus(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    ALARM = "alarm"


class FaultSeverity(str, Enum):
    WARNING = "warning"
    ALARM = "alarm"
    CRITICAL = "critical"


class AssessmentResult(BaseModel):
    """Per-parameter assessment."""

    parameter_name: str
    current_value: float
    status: ParameterStatus
    severity_score: float = Field(ge=0, le=1)
    health_score: float = Field(default=1.0, ge=0, le=1, description="Health score (1=perfect, 0=critical)")
    normal_range: str
    message: str


class GradedRecommendation(BaseModel):
    """A recommendation with urgency level."""

    text: str
    level: str = "long_term"  # immediate / long_term / preventive


class DiagnosedFault(BaseModel):
    """A diagnosed fault with confidence and recommendations."""

    fault_type: str
    confidence: float = Field(ge=0, le=1)
    matched_rules: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    severity: FaultSeverity = FaultSeverity.WARNING
    description: str = ""
    causal_chain: Optional[str] = None
    recommendations: List[GradedRecommendation] = Field(default_factory=list)


class DiagnosisResult(BaseModel):
    """Complete diagnosis result."""

    reactor_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    parameter_assessments: List[AssessmentResult] = Field(default_factory=list)
    overall_status: ParameterStatus = ParameterStatus.NORMAL
    faults: List[DiagnosedFault] = Field(default_factory=list)
    recommendations: List[GradedRecommendation] = Field(default_factory=list)
    llm_analysis: Optional[str] = None
    llm_model: Optional[str] = None

    @property
    def is_healthy(self) -> bool:
        return self.overall_status == ParameterStatus.NORMAL and len(self.faults) == 0

    @property
    def fault_count(self) -> int:
        return len(self.faults)
